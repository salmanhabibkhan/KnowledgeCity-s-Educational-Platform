from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    STAGE: Optional[str] = "prod"
    APP_NAME: Optional[str] = "knowledgecity-video-processing"
    SERVICE_NAME: Optional[str] = "kc-video-processing"

    @property
    def APP_PREFIX(self):
        return f'{self.APP_NAME}-{self.STAGE}'

    @property
    def APP_NAME_IN_PASCAL_CASE(self):
        return ''.join(word.capitalize() for word in self.APP_PREFIX.split('-'))

class ChartSettings(Settings): # Use this class for chart related settings
    ECR_ACCOUNT: Optional[str] = None
    TAG: Optional[str] = "latest"
    VOLUME_MOUNT_PATH: Optional[str] = "/mnt/data"
    APP_PORT: Optional[int] = 80
    SERVICE_TYPE: Optional[str] = "NodePort"
    REPLICAS: Optional[int] = 1
    VERSION: Optional[str] = "latest"

    @property
    def IMAGE_TAG(self):
        return f"{self.ECR_ACCOUNT}/{self.APP_NAME}:{self.VERSION}"

class AppSettings(ChartSettings):  # Use this class for app variable settings

    DATABASE_URL: Optional[str] = None

    def get_app_config_map_data(self):
        app_config_map_data = {
            'DATABASE_URL': self.DATABASE_URL,
        }

        return app_config_map_data

settings = AppSettings()
