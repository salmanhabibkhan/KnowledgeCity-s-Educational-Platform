from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    STAGE: Optional[str] = 'prod'
    APP_NAME: Optional[str] = 'rabbitmq'
    SERVICE_NAME: Optional[str] = 'rabbitmq'

    @property
    def APP_PREFIX(self):
        return f'{self.APP_NAME}-{self.STAGE}'

    @property
    def APP_NAME_IN_PASCAL_CASE(self):
        return ''.join(word.capitalize() for word in self.APP_PREFIX.split('-'))

class ChartSettings(Settings): # Use this class for chart related settings
    TAG: Optional[str] = 'latest'
    APP_PORT: Optional[int] = 5672
    SERVICE_TYPE: Optional[str] = 'NodePort'
    REPLICAS: Optional[int] = 1
    IMAGE_TAG: Optional[str] = 'rabbitmq:4-management'
    VERSION: Optional[str] = 'latest'
    VOLUME_MOUNT_PATH: Optional[str] = '/etc/config'

class AppSettings(ChartSettings):  # Use this class for app variable settings
    # CELERY_BROKER_URL: Optional[str] = 'amqp://guest:guest@rabbitmq.feat.svc.cluster.local:5672//'

    def get_app_config_map_data(self):
        app_config_map_data = {
            'STAGE': self.STAGE,
        }

        return app_config_map_data

settings = AppSettings()
