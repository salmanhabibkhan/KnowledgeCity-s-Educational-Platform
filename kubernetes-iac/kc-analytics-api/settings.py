from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    STAGE: Optional[str] = "prod"
    APP_NAME: Optional[str] = "knowledgecity-analytics"
    SERVICE_NAME: Optional[str] = "kc-analytics"
    ACCOUNT_INFO: Optional[str] = None

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

    REVISION_HISTORY_LIMIT: Optional[int] = 3
    TERMINATION_GRACE_PERIOD_SECONDS: Optional[int] = 30
    POD_CPU_RESOURCE_REQUEST: Optional[str] = '100m'
    POD_MEMORY_RESOURCE_REQUEST: Optional[str] = '150Mi'
    POD_CPU_RESOURCE_LIMIT: Optional[str] = '200m'
    POD_MEMORY_RESOURCE_LIMIT: Optional[str] = '300Mi'
    HPA_MIN_REPLICAS: Optional[int] = 1
    HPA_MAX_REPLICAS: Optional[int] = 2
    METRIC_AVERAGE_CPU_UTILIZATION: Optional[int] = 70
    METRIC_AVERAGE_MEMORY_UTILIZATION: Optional[int] = 70

    @property
    def IMAGE_TAG(self):
        return f"{self.ECR_ACCOUNT}/{self.APP_NAME}:{self.VERSION}"

class AppSettings(ChartSettings): # Use this class for app variable settings
    STAGE: Optional[str] = "prod"
    DATABASE_URL: Optional[str] = None

    def get_app_config_map_data(self):
        """
        Returns configuration values only from AppSettings class as a dictionary
        Excludes inherited attributes from parent classes
        """
        app_settings_attrs = set(AppSettings.__annotations__.keys())
        
        config_map_data = {
            key: getattr(self, key)
            for key in app_settings_attrs
            if hasattr(self, key) and not key.startswith('_')
        }
        
        return config_map_data

settings = AppSettings()