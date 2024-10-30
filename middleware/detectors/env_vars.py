import os
from opentelemetry.sdk.resources import Resource, ResourceDetector

ENV_ATTR_NAME = "process.environ"


class EnvVarsDetector(ResourceDetector):
    def detect(self) -> "Resource":
        resource_info = {
            ENV_ATTR_NAME: str(dict(os.environ)),
        }
        return Resource(resource_info)
