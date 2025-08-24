from constructs import Construct
from imports import k8s
from settings import settings
from typing import Dict, Any

def create_hpa(scope: Construct, values: Dict[str, Any]) -> k8s.KubeConfigMap:
    app_name = settings.APP_NAME
    stage = settings.STAGE
    app_name_pascal = settings.APP_NAME_IN_PASCAL_CASE

    hpa = k8s.KubeHorizontalPodAutoscalerV2(scope, f'{app_name_pascal}HPA',
        metadata=k8s.ObjectMeta(
            name=f'{app_name}-hpa',
            namespace=stage,
            labels={**values}
        ),
        spec=k8s.HorizontalPodAutoscalerSpecV2(
            min_replicas=settings.HPA_MIN_REPLICAS,
            max_replicas=settings.HPA_MAX_REPLICAS,
            scale_target_ref=k8s.CrossVersionObjectReferenceV2(
                api_version='apps/v1',
                kind='Deployment',
                name=app_name
            ),
            metrics=[
                k8s.MetricSpecV2(
                    type='Resource',
                    resource=k8s.ResourceMetricSourceV2(
                        name='cpu',
                        target=k8s.MetricTargetV2(
                            type='AverageValue',
                            average_utilization=settings.METRIC_AVERAGE_CPU_UTILIZATION
                        )
                    )
                ),
                k8s.MetricSpecV2(
                    type='Resource',
                    resource=k8s.ResourceMetricSourceV2(
                        name='memory',
                        target=k8s.MetricTargetV2(
                            type='AverageValue',
                            average_utilization=settings.METRIC_AVERAGE_MEMORY_UTILIZATION
                        )
                    )
                )
            ]
        )
    )

    return hpa