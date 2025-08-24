from constructs import Construct
from cdk8s import App, Chart
from settings import settings
from typing import Dict, Any

from charts.config_map import create_config_map
from charts.service import create_service
from charts.deployment import create_deployment
from charts.hpa import create_hpa

class AnalyticsApiChart(Chart):
    def __init__(self, scope: Construct, id: str, values: Dict[str, Any] = None):
        super().__init__(scope, id)
        values = values or {}

        create_config_map(self, values)
        create_service(self, values)
        create_deployment(self, values)
        if settings.ACCOUNT_INFO == 'prod':
            create_hpa(self, values)

app = App()
values = {
    f'{settings.APP_NAME}': settings.VERSION,
}
AnalyticsApiChart(app, settings.SERVICE_NAME, values=values)
app.synth()
