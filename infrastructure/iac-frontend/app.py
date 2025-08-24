#!/usr/bin/env python3

import aws_cdk as cdk

from iac.iac_stack import IacStack
from settings import settings

app = cdk.App()
iac_stack = IacStack(
    app,
    f"kc-{settings.service_name}-{settings.stage.value}-stack",
    env=cdk.Environment(account=settings.account, region=settings.region),
    service_name=settings.service_name,
    stage=settings.stage
)

cdk.Tags.of(iac_stack).add("Environment", settings.stage.value)

app.synth()
