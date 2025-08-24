from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as cloudfront_origins,
    aws_s3_deployment as s3_deployment, RemovalPolicy,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as route53_targets, CfnOutput,
)
from constructs import Construct

from settings import settings

from enums import Stage


class IacStack(Stack):
    service_name: str
    stage: Stage
    stack_prefix: str

    def __init__(
            self, scope: Construct, construct_id: str,
            service_name='kc-frontend',
            stage=Stage('dev'),
            **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.service_name = service_name
        self.stage = stage
        self.stack_prefix = f'kc-{self.service_name}-{self.stage.value}'

        site_bucket = self.create_site_bucket()

        origin = self.create_origin_group(self, site_bucket=site_bucket)

        distribution = self.create_distribution(
            origin=origin
        )

        self.create_deployment(
            site_bucket=site_bucket,
            distribution=distribution
        )

    def create_site_bucket(self):
        site_bucket_name = f'{self.stack_prefix}-{Stack.of(self).account}-{Stack.of(self).region}-site-bucket'

        site_bucket = s3.Bucket(
            self, site_bucket_name,
            bucket_name=site_bucket_name,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            cors=[s3.CorsRule(
                allowed_methods=[
                    s3.HttpMethods.GET,
                    s3.HttpMethods.POST,
                    s3.HttpMethods.PUT,
                    s3.HttpMethods.DELETE,
                    s3.HttpMethods.HEAD,
                ],
                allowed_origins=["*"],
                allowed_headers=["*"]
            )]
        )

        return site_bucket

    @staticmethod
    def create_origin_group(self, site_bucket: s3.Bucket):
        oai_id = 'kcmfeOaiId'
        oai = cloudfront.OriginAccessIdentity(self, oai_id, comment="Origin Access Identity")
        origin = cloudfront_origins.OriginGroup(
            primary_origin=cloudfront_origins.S3Origin(site_bucket, origin_access_identity=oai),
            fallback_origin=cloudfront_origins.S3Origin(site_bucket, origin_access_identity=oai),
            fallback_status_codes=[404]
        )

        return origin

    def create_distribution(
            self,
            origin: cloudfront_origins.OriginGroup
    ):
        certificate = acm.Certificate.from_certificate_arn(
            self, f'{self.stack_prefix}-dns-validated-ssl-certificate',
            certificate_arn=settings.certificate_arn
        )

        hosted_zone = route53.HostedZone.from_lookup(
            self, f'{self.stack_prefix}-hosted-zone-with-attributes',
            domain_name=settings.hosted_zone_name
        )

        distribution = cloudfront.Distribution(
            self, f'{settings.service_name}-distribution',
            certificate=certificate,
            comment=self.stack_prefix,
            default_root_object='index.html',

            domain_names=[
                settings.get_domain(),
            ],
            default_behavior=cloudfront.BehaviorOptions(
                origin=origin,
                response_headers_policy=cloudfront.ResponseHeadersPolicy.CORS_ALLOW_ALL_ORIGINS,
            ),
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html"
                )
            ]
        )

        route53.ARecord(
            self, f'{self.stack_prefix}-dn-alias-record',
            record_name=settings.get_domain(),
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(route53_targets.CloudFrontTarget(distribution))
        )

        CfnOutput(
            self, "DistributionId",
            value=distribution.distribution_id,
            export_name=f'{self.stack_prefix}-distribution-id'
        )

        CfnOutput(
            self, "DistributionDomainName",
            value=distribution.distribution_domain_name,
            export_name=f'{self.stack_prefix}-distribution-domain-name'
        )

        return distribution

    def create_deployment(self, site_bucket: s3.Bucket, distribution: cloudfront.Distribution):
        s3_deployment.BucketDeployment(
            self, 'deploy-with-invalidation',
            sources=[
                s3_deployment.Source.asset('../dist'),
                s3_deployment.Source.asset('../src'),
                s3_deployment.Source.asset('../public')
                ],
            destination_bucket=site_bucket,
            distribution=distribution,
            distribution_paths=['/*'],
            prune=False
        )
