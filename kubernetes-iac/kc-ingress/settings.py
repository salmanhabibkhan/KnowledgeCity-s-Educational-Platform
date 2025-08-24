from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))


class Settings(BaseSettings):
    STAGE: Optional[str] = "prod"
    APP_NAME: Optional[str] = "knowledgecity-ingress"
    SERVICE_NAME: Optional[str] = "kc-ingress"

    @property
    def APP_PREFIX(self):
        return f'{self.APP_NAME}-{self.STAGE}'

    @property
    def APP_NAME_IN_PASCAL_CASE(self):
        return ''.join(word.capitalize() for word in self.APP_PREFIX.split('-'))


class AppSettings(Settings):
    INGRESS_CLASS: Optional[str] = "kc-ingress"
    INGRESS_HOST: Optional[str] = "api-k8s-usa.knowledgecity.com"
    RABBITMQ_HOST: Optional[str] = "rabbitmq-k8s-usa.knowledgecity.com"
    CELERY_HOST: Optional[str] = "celery-k8s-usa.knowledgecity.com"
    APP_PORT: Optional[int] = 80
    CERTIFICATE_ARN: Optional[str] = "arn:aws:acm:us-east-1:123456789012:certificate/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"


    def get_ingress_service_paths(self):
        return {
            'kc-monolith-api': ['/monolith/*'],
            'kc-analytics-api': ['/analytics/*'],
            'kc-vp-api': ['/vp/*'],
        }

    def get_service_ports(self):
        return {
            'celery': 5555,
            'rabbitmq': 15672,  # RabbitMQ management UI port
            'redis': 6379,
        }

    def get_auth_ingress_service_path(self):
        return '/auth(/|$)(.*)'

    def get_ingress_annotations(self):
        return {
            # AWS ALB Ingress Annotations
            'kubernetes.io/ingress.class': f'{self.INGRESS_CLASS}',
            'alb.ingress.kubernetes.io/scheme': 'internet-facing',
            'alb.ingress.kubernetes.io/target-type': 'instance',
            'alb.ingress.kubernetes.io/listen-ports': '[{"HTTP": 80}, {"HTTPS": 443}]',
            'alb.ingress.kubernetes.io/certificate-arn': f'{self.CERTIFICATE_ARN}',
            'alb.ingress.kubernetes.io/ssl-policy': 'ELBSecurityPolicy-TLS13-1-2-2021-06',
            'alb.ingress.kubernetes.io/backend-protocol': 'HTTP',
            'alb.ingress.kubernetes.io/ssl-redirect': '443',
            'alb.ingress.kubernetes.io/healthcheck-path': '/health',
            'alb.ingress.kubernetes.io/healthcheck-interval-seconds': '300',
            'alb.ingress.kubernetes.io/healthcheck-timeout-seconds': '5',
            'alb.ingress.kubernetes.io/healthy-threshold-count': '2',
            'alb.ingress.kubernetes.io/unhealthy-threshold-count': '2',
            'alb.ingress.kubernetes.io/success-codes': '200,404'
        }


settings = AppSettings()
