from constructs import Construct
from cdk8s import App, Chart
from imports import k8s
from settings import settings
from typing import Dict, Any

class CeleryChart(Chart):
    def __init__(self, scope: Construct, id: str, values: Dict[str, Any] = None):
        super().__init__(scope, id)
   
        self.values = values

        stage = settings.STAGE
        app_name = settings.APP_NAME
        app_name_in_pascal_case = settings.APP_NAME_IN_PASCAL_CASE
        app_port = settings.APP_PORT
        service_type = settings.SERVICE_TYPE
        replicas = settings.REPLICAS

        label = { 'app': app_name }
 
        config_map = k8s.KubeConfigMap(self, f'{app_name_in_pascal_case}ConfigMap',
            metadata=k8s.ObjectMeta(
                name=f'{app_name}-config-map',
                namespace=stage,
                labels={
                    **self.values,
                }
            ),
            data=settings.get_app_config_map_data(),
        )

        service = k8s.KubeService(self, f'{app_name_in_pascal_case}Service',
            metadata=k8s.ObjectMeta(
                namespace=stage,
                name=app_name,
                labels={
                    **self.values,
                }
            ),
            spec=k8s.ServiceSpec(
                selector=label,
                type=service_type,
                ports=[k8s.ServicePort(port=app_port, target_port=k8s.IntOrString.from_number(app_port))]
            )
        )
 
        deployment = k8s.KubeDeployment(self, f'{app_name_in_pascal_case}Deployment',
            metadata=k8s.ObjectMeta(
                namespace=stage,
                name=app_name,
                labels={
                    **self.values,
                },
            ),
            spec=k8s.DeploymentSpec(
                replicas=replicas,
                selector=k8s.LabelSelector(match_labels=label),
                template=k8s.PodTemplateSpec(
                    metadata=k8s.ObjectMeta(
                        labels={
                            **label,
                            **self.values,
                        },
                    ),
                    spec=k8s.PodSpec(
                        containers=[
                            k8s.Container(
                                name=app_name,
                                image=settings.IMAGE_TAG,
                                image_pull_policy='Always',
                                ports=[k8s.ContainerPort(container_port=app_port)],
                                env=[
                                    k8s.EnvVar(
                                        name='CHART_VERSION',
                                        value=self.values[f'{settings.APP_NAME}']
                                    )
                                ],
                                env_from=[
                                    k8s.EnvFromSource(
                                        config_map_ref=k8s.ConfigMapEnvSource(
                                            name=f'{app_name}-config-map'
                                        )
                                    )
                                ],                                
                                volume_mounts=[
                                    k8s.VolumeMount(
                                        name=f'{app_name}-config-map-volume',
                                        mount_path=settings.VOLUME_MOUNT_PATH
                                    )
                                ]
                            )
                        ],
                        volumes=[
                            k8s.Volume(
                                name=f'{app_name}-config-map-volume',
                                config_map=k8s.ConfigMapVolumeSource(name=f'{app_name}-config-map')
                            )
                        ]
                    )
                )
            )
        )
 
app = App()

values = {
    f'{settings.APP_NAME}': settings.VERSION,
}

CeleryChart(app, settings.SERVICE_NAME, values=values)
app.synth()