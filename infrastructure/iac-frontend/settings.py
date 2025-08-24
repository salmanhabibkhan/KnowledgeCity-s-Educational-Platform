from pydantic import BaseSettings, Field

from enums import Stage


class Settings(BaseSettings):
    """
    set -o allexport; source .env; set +o allexport
    """
    stage: str = Field("dev", env="STAGE")
    service_name: str = Field("knowledgecity-mfe", env="SERVICE_NAME")
    region: str = Field("us-east-1", env="AWS_DEFAULT_REGION")
    account: str = Field("123456789012", env="CDK_DEFAULT_ACCOUNT")

    hosted_zone_id: str = Field("Z123456789ABC", env="ROUTE_53_HOSTED_ZONE_ID")
    hosted_zone_name: str = Field("knowledgecity.com", env="ROUTE_53_HOSTED_ZONE_NAME")
    certificate_arn: str = Field(
        "arn:aws:acm:us-east-1:123456789012:certificate/abc12345-6789-def0-1234-56789abcdef0",
        env="ROUTE_53_CERTIFICATE_ARN"
    )

    def get_domain(self):
        if self.stage == Stage.prod:
            return f'{self.service_name}.{self.hosted_zone_name}'

        return f'{self.service_name}-{self.stage.value}.{self.hosted_zone_name}'


settings = Settings()
