from constructs import Construct
from cdk8s import App, Chart
from imports import k8s
from settings import settings
from typing import Dict, Any

class RedisChart(Chart):
    def __init__(self, scope: Construct, id: str, values: Dict[str, Any] = None):
        super().__init__(scope, id)

        self.values = values

        # Extract settings
        stage = settings.STAGE
        app_name = settings.APP_NAME
        app_name_in_pascal_case = settings.APP_NAME_IN_PASCAL_CASE
        app_port = settings.APP_PORT
        service_type = settings.SERVICE_TYPE
        replicas = settings.REPLICAS
        volume_mount_path = settings.VOLUME_MOUNT_PATH
        pvc_storage = settings.PVC_STORAGE
        redis_image = f"{settings.REDIS_IMAGE}:{settings.VERSION}"

        # Labels for resources
        label = { 'app': app_name }

        # Create a PersistentVolumeClaim for Redis data
        pvc = k8s.KubePersistentVolumeClaim(self, f'{app_name_in_pascal_case}Pvc',
            metadata=k8s.ObjectMeta(
                name=f'{app_name}-pvc',
                namespace=stage,
                labels=label
            ),
            spec=k8s.PersistentVolumeClaimSpec(
                access_modes=['ReadWriteOnce'],
                resources=k8s.ResourceRequirements(
                    requests={
                        'storage': k8s.Quantity.from_string(pvc_storage)  # Use Quantity for storage
                    }
                )
            )
        )

        # Create a Service for Redis
        service = k8s.KubeService(self, f'{app_name_in_pascal_case}Service',
            metadata=k8s.ObjectMeta(
                namespace=stage,
                name=app_name,
                labels=label
            ),
            spec=k8s.ServiceSpec(
                selector=label,
                type=service_type,
                ports=[k8s.ServicePort(port=app_port, target_port=k8s.IntOrString.from_number(app_port))]
            )
        )

        # Create a Deployment for Redis
        deployment = k8s.KubeDeployment(self, f'{app_name_in_pascal_case}Deployment',
            metadata=k8s.ObjectMeta(
                namespace=stage,
                name=app_name,
                labels=label
            ),
            spec=k8s.DeploymentSpec(
                replicas=replicas,
                selector=k8s.LabelSelector(match_labels=label),
                template=k8s.PodTemplateSpec(
                    metadata=k8s.ObjectMeta(
                        labels=label
                    ),
                    spec=k8s.PodSpec(
                        containers=[
                            k8s.Container(
                                name=app_name,
                                image=redis_image,
                                ports=[k8s.ContainerPort(container_port=app_port)],
                                volume_mounts=[
                                    k8s.VolumeMount(
                                        name=f'{app_name}-data',
                                        mount_path=volume_mount_path
                                    )
                                ]
                            )
                        ],
                        volumes=[
                            k8s.Volume(
                                name=f'{app_name}-data',
                                persistent_volume_claim=k8s.PersistentVolumeClaimVolumeSource(
                                    claim_name=pvc.name
                                )
                            )
                        ]
                    )
                )
            )
        )

# Create the CDK8s app
app = App()

# Define dynamic values
values = {
    f'{settings.APP_NAME}': settings.VERSION,
}

# Synthesize the Redis chart
RedisChart(app, settings.SERVICE_NAME, values=values)

# Generate Kubernetes manifests
app.synth()