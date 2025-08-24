from constructs import Construct
from imports import k8s
from settings import settings
from typing import Dict, Any

def create_deployment(scope: Construct, values: Dict[str, Any]) -> k8s.KubeDeployment:
    app_name = settings.APP_NAME
    stage = settings.STAGE
    app_name_pascal = settings.APP_NAME_IN_PASCAL_CASE
    app_port = settings.APP_PORT
    replicas = settings.REPLICAS

    revision_history_limit = settings.REVISION_HISTORY_LIMIT
    termination_grace_period_seconds = settings.TERMINATION_GRACE_PERIOD_SECONDS
    pod_cpu_resource_request = settings.POD_CPU_RESOURCE_REQUEST
    pod_memory_resource_request = settings.POD_MEMORY_RESOURCE_REQUEST
    pod_cpu_resource_limit = settings.POD_CPU_RESOURCE_LIMIT
    pod_memory_resource_limit = settings.POD_MEMORY_RESOURCE_LIMIT

    label = {'app': app_name}

    # Prepare container arguments
    container_args = {
        "name": app_name,
        "image": settings.IMAGE_TAG,
        "image_pull_policy": 'Always',
        "ports": [k8s.ContainerPort(container_port=app_port)],
        "env": [
            k8s.EnvVar(
                name='CHART_VERSION',
                value=values.get(app_name)
            )
        ],
        "env_from": [
            k8s.EnvFromSource(
                config_map_ref=k8s.ConfigMapEnvSource(
                    name=f'{app_name}-config-map'
                )
            )
        ],
        "volume_mounts": [
            k8s.VolumeMount(
                name=f'{app_name}-config-map-volume',
                mount_path=settings.VOLUME_MOUNT_PATH
            )
        ]
    }

    # Add resource requirements only if ACCOUNT_INFO is 'bmw'
    if settings.ACCOUNT_INFO == 'bmw':
        container_args["resources"] = k8s.ResourceRequirements(
            requests={
                'cpu': k8s.Quantity.from_string(pod_cpu_resource_request),
                'memory': k8s.Quantity.from_string(pod_memory_resource_request)
            },
            limits={
                'cpu': k8s.Quantity.from_string(pod_cpu_resource_limit),
                'memory': k8s.Quantity.from_string(pod_memory_resource_limit)
            }
        )

    return k8s.KubeDeployment(scope, f'{app_name_pascal}Deployment',
        metadata=k8s.ObjectMeta(
            namespace=stage,
            name=app_name,
            labels={**values}
        ),
        spec=k8s.DeploymentSpec(
            replicas=1 if settings.ACCOUNT_INFO == 'bmw' else replicas,
            revision_history_limit=revision_history_limit,
            selector=k8s.LabelSelector(match_labels=label),
            template=k8s.PodTemplateSpec(
                metadata=k8s.ObjectMeta(
                    labels={**label, **values}
                ),
                spec=k8s.PodSpec(
                    termination_grace_period_seconds=termination_grace_period_seconds,
                    containers=[
                        k8s.Container(**container_args)
                    ],
                    volumes=[
                        k8s.Volume(
                            name=f'{app_name}-config-map-volume',
                            config_map=k8s.ConfigMapVolumeSource(
                                name=f'{app_name}-config-map'
                            )
                        )
                    ]
                )
            )
        )
    )
