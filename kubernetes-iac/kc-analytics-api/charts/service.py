from constructs import Construct
from imports import k8s
from settings import settings
from typing import Dict, Any

def create_service(scope: Construct, values: Dict[str, Any]) -> k8s.KubeService:
    app_name = settings.APP_NAME
    stage = settings.STAGE
    app_name_pascal = settings.APP_NAME_IN_PASCAL_CASE
    app_port = settings.APP_PORT
    service_type = settings.SERVICE_TYPE

    label = {'app': app_name}

    return k8s.KubeService(scope, f'{app_name_pascal}Service',
        metadata=k8s.ObjectMeta(
            namespace=stage,
            name=app_name,
            labels={**values}
        ),
        spec=k8s.ServiceSpec(
            selector=label,
            type=service_type,
            ports=[k8s.ServicePort(port=app_port, target_port=k8s.IntOrString.from_number(app_port))]
        )
    )
