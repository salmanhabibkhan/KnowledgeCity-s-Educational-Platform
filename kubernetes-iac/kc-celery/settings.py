from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    STAGE: Optional[str] = 'prod'
    APP_NAME: Optional[str] = 'celery'
    SERVICE_NAME: Optional[str] = 'celery'

    @property
    def APP_PREFIX(self):
        return f'{self.APP_NAME}-{self.STAGE}'

    @property
    def APP_NAME_IN_PASCAL_CASE(self):
        return ''.join(word.capitalize() for word in self.APP_PREFIX.split('-'))

class ChartSettings(Settings): # Use this class for chart related settings
    TAG: Optional[str] = 'latest'
    APP_PORT: Optional[int] = 5555
    SERVICE_TYPE: Optional[str] = 'NodePort'
    REPLICAS: Optional[int] = 1
    IMAGE_TAG: Optional[str] = "mher/flower"
    VERSION: Optional[str] = 'latest'
    VOLUME_MOUNT_PATH: Optional[str] = '/etc/config'

class AppSettings(ChartSettings):  # Use this class for app variable settings
    @property
    def CELERY_BROKER_URL(self) -> str:
        return f'amqp://guest:guest@rabbitmq.{self.STAGE}.svc.cluster.local:5672//'

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return f'redis://kc-redis.{self.STAGE}.svc.cluster.local:6379/0'

    def get_app_config_map_data(self):
        app_config_map_data = {
            'STAGE': self.STAGE,
            'CELERY_BROKER_URL': self.CELERY_BROKER_URL,
            'CELERY_RESULT_BACKEND': self.CELERY_RESULT_BACKEND,
        }

        return app_config_map_data

settings = AppSettings()
