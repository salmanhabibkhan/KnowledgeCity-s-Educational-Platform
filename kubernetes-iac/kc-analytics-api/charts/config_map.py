from constructs import Construct
from imports import k8s
from settings import settings
from typing import Dict, Any

def create_config_map(scope: Construct, values: Dict[str, Any]) -> k8s.KubeConfigMap:
    app_name = settings.APP_NAME
    stage = settings.STAGE
    app_name_pascal = settings.APP_NAME_IN_PASCAL_CASE

    return k8s.KubeConfigMap(scope, f'{app_name_pascal}ConfigMap',
        metadata=k8s.ObjectMeta(
            name=f'{app_name}-config-map',
            namespace=stage,
            labels={**values}
        ),
        data=settings.get_app_config_map_data(),
    )
