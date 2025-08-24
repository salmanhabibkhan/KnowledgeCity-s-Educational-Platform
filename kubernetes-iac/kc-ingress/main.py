from constructs import Construct
from cdk8s import App, Chart
from imports import k8s
from settings import settings


class IngressChart(Chart):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        stage = settings.STAGE
        app_name = settings.APP_NAME
        app_name_in_pascal_case = settings.APP_NAME_IN_PASCAL_CASE

        ingress_label = {'app': app_name}

        self.create_namespace(app_name_in_pascal_case, stage)
        self.create_ingress(stage, ingress_label)

    def create_namespace(self, app_name_in_pascal_case, stage):
        k8s.KubeNamespace(self, f'{app_name_in_pascal_case}Namespace',
                          metadata=k8s.ObjectMeta(
                              name=stage,
                          )
                          )

    def create_ingress(self, stage, ingress_label):
        annotations = settings.get_ingress_annotations()

        ingress = k8s.KubeIngress(self, settings.APP_NAME_IN_PASCAL_CASE,
                                  metadata=k8s.ObjectMeta(
                                      name=settings.APP_PREFIX,
                                      namespace=stage,
                                      annotations=dict(annotations),
                                      labels=ingress_label
                                  ),
                                  spec=k8s.IngressSpec(
                                      ingress_class_name=settings.INGRESS_CLASS,
                                      rules=[
                                          # Main API rule
                                          k8s.IngressRule(
                                              host=settings.INGRESS_HOST,
                                              http=k8s.HttpIngressRuleValue(
                                                  paths=[
                                                      path for service, paths in settings.get_ingress_service_paths().items()
                                                      for path in self.create_http_ingress_paths(service, paths)
                                                  ]
                                              )
                                          ),
                                          # RabbitMQ subdomain rule
                                          k8s.IngressRule(
                                              host=settings.RABBITMQ_HOST,  # RabbitMQ subdomain
                                              http=k8s.HttpIngressRuleValue(
                                                  paths=[
                                                      k8s.HttpIngressPath(
                                                          path="/*",
                                                          path_type='ImplementationSpecific',
                                                          backend=k8s.IngressBackend(
                                                              service=k8s.IngressServiceBackend(
                                                                  name='rabbitmq',  # RabbitMQ service name
                                                                  port=k8s.ServiceBackendPort(
                                                                      number=15672)  # RabbitMQ management UI port
                                                              )
                                                          )
                                                      ),
                                                      k8s.HttpIngressPath(
                                                          path="/*",
                                                          path_type='ImplementationSpecific',
                                                          backend=k8s.IngressBackend(
                                                              service=k8s.IngressServiceBackend(
                                                                  name='rabbitmq',  # RabbitMQ service name
                                                                  port=k8s.ServiceBackendPort(
                                                                      number=5672)  # RabbitMQ management UI port
                                                              )
                                                          )
                                                      )
                                                  ]
                                              )
                                          ),
                                          k8s.IngressRule(
                                              host=settings.CELERY_HOST,
                                              http=k8s.HttpIngressRuleValue(
                                                  paths=[
                                                      k8s.HttpIngressPath(
                                                          path="/*",
                                                          path_type='ImplementationSpecific',
                                                          backend=k8s.IngressBackend(
                                                              service=k8s.IngressServiceBackend(
                                                                  name='celery',
                                                                  port=k8s.ServiceBackendPort(
                                                                      number=5555)
                                                              )
                                                          )
                                                      )
                                                  ]
                                              )
                                          ),
                                      ]
                                  )
                                  )

    def create_http_ingress_paths(self, service_name, paths):
        # Get service-specific port, default to APP_PORT if not found
        service_ports = settings.get_service_ports()
        port = service_ports.get(service_name, settings.APP_PORT)

        # Return a list of HttpIngressPath for each path pattern
        return [
            k8s.HttpIngressPath(
                path=path,
                path_type='ImplementationSpecific',
                backend=k8s.IngressBackend(
                    service=k8s.IngressServiceBackend(
                        name=service_name,
                        port=k8s.ServiceBackendPort(number=port)
                    )
                )
            )
            for path in paths
        ]

app = App()
IngressChart(app, settings.SERVICE_NAME)
app.synth()