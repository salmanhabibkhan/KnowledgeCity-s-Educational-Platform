from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    STAGE: Optional[str] = "prod"
    APP_NAME: Optional[str] = "kc-redis"
    SERVICE_NAME: Optional[str] = "redis-service"

    @property
    def APP_PREFIX(self):
        return f"{self.APP_NAME}-{self.STAGE}"

    @property
    def APP_NAME_IN_PASCAL_CASE(self):
        return "".join(word.capitalize() for word in self.APP_PREFIX.split("-"))

class ChartSettings(Settings):
    VOLUME_MOUNT_PATH: Optional[str] = "/data"  # Redis data directory
    APP_PORT: Optional[int] = 6379  # Redis container port
    SERVICE_PORT: Optional[int] = 6379  # Redis service port
    SERVICE_TYPE: Optional[str] = "NodePort"  # Service type
    REPLICAS: Optional[int] = 1  # Number of Redis replicas
    VERSION: Optional[str] = "latest"  # Redis image version
    PVC_STORAGE: Optional[str] = "1Gi"  # Persistent storage size
    REDIS_IMAGE: Optional[str] = "redis"  # Redis Docker image

settings = ChartSettings()
class Settings(BaseSettings):
    STAGE: Optional[str] = "prod"
    APP_NAME: Optional[str] = "kc-redis"
    SERVICE_NAME: Optional[str] = "redis-service"

    @property
    def APP_PREFIX(self):
        return f"{self.APP_NAME}-{self.STAGE}"

    @property
    def APP_NAME_IN_PASCAL_CASE(self):
        return "".join(word.capitalize() for word in self.APP_PREFIX.split("-"))

class ChartSettings(Settings):
    VOLUME_MOUNT_PATH: Optional[str] = "/data"  # Redis data directory
    APP_PORT: Optional[int] = 6379  # Redis container port
    SERVICE_PORT: Optional[int] = 6379  # Redis service port
    SERVICE_TYPE: Optional[str] = "NodePort"  # Service type
    REPLICAS: Optional[int] = 1  # Number of Redis replicas
    VERSION: Optional[str] = "latest"  # Redis image version
    PVC_STORAGE: Optional[str] = "1Gi"  # Persistent storage size
    REDIS_IMAGE: Optional[str] = "redis"  # Redis Docker image

settings = ChartSettings()