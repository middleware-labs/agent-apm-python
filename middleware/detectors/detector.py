import logging
from enum import Enum
from typing import Union, List
from middleware.detectors.env_vars import EnvVarsDetector
from opentelemetry.resource.detector.azure.app_service import (
    AzureAppServiceResourceDetector,
)
from opentelemetry.resource.detector.azure.vm import AzureVMResourceDetector
from opentelemetry.resource.detector.azure.functions import (
    AzureFunctionsResourceDetector,
)
from opentelemetry.sdk.extension.aws.resource.ecs import AwsEcsResourceDetector
from opentelemetry.sdk.extension.aws.resource._lambda import AwsLambdaResourceDetector
from opentelemetry.sdk.extension.aws.resource.beanstalk import (
    AwsBeanstalkResourceDetector,
)
from opentelemetry.sdk.extension.aws.resource.ec2 import AwsEc2ResourceDetector
from opentelemetry.sdk.extension.aws.resource.eks import AwsEksResourceDetector
from opentelemetry.resourcedetector.gcp_resource_detector._detector import (
    GoogleCloudResourceDetector,
)

_logger = logging.getLogger(__name__)


# Define an enumeration
class Detector(Enum):
    ENVVARS = "envvars"
    AWS_LAMBDA = "aws_lambda"
    AWS_BEANSTALK = "aws_beanstalk"
    AWS_ECS = "aws_ecs"
    AWS_EKS = "aws_eks"
    AWS_EC2 = "aws_ec2"

    AZURE_VM = "azure_vm"
    AZURE_APP_SERVICE = "azure_app_service"
    AZURE_FUNCTIONS = "azure_functions"

    GCP = "gcp"


def process_detector_input(input_value: Union[str, List[Detector]]):
    """
    This function takes either a string of comma-separated detectors names
    or a list of Detector enum members and returns a list of Detector enum members.
    """
    unique_detectors = set()
    # If input is a string, split it into a list
    if isinstance(input_value, str):
        items = [item.strip() for item in input_value.split(",")]

        for item in items:
            try:
                # Attempt to access the enum member using the string
                enum_value = Detector[item.upper()]  # Convert to uppercase for matching
                unique_detectors.add(enum_value)
            except KeyError:
                _logger.warning(f"{item} is not a valid Detector")

    # If input is already a list, ensure it contains Detector enums
    elif isinstance(input_value, list):
        if all(isinstance(item, Detector) for item in input_value):
            unique_detectors.update(input_value)
        else:
            raise ValueError("All items in the list must be instances of Detector Enum")

    else:
        raise TypeError(
            "Input must be either a string or a list of Detector Enum members"
        )

    return list(unique_detectors)


def get_detectors(detectors: List[Detector]):
    resource_detectors = set()

    if detectors is not None and len(detectors) != 0:
        for detector in detectors:
            if detector == Detector.ENVVARS:
                resource_detectors.add(EnvVarsDetector())
            elif detector == Detector.AWS_LAMBDA:
                resource_detectors.add(AwsLambdaResourceDetector())
            elif detector == Detector.AWS_BEANSTALK:
                resource_detectors.add(AwsBeanstalkResourceDetector())
            elif detector == Detector.AWS_ECS:
                resource_detectors.add(AwsEcsResourceDetector())
            elif detector == Detector.AWS_EKS:
                resource_detectors.add(AwsEksResourceDetector())
            elif detector == Detector.AWS_EC2:
                resource_detectors.add(AwsEc2ResourceDetector())
            elif detector == Detector.AZURE_VM:
                resource_detectors.add(AzureVMResourceDetector())
            elif detector == Detector.AZURE_APP_SERVICE:
                resource_detectors.add(AzureAppServiceResourceDetector())
            elif detector == Detector.AZURE_FUNCTIONS:
                resource_detectors.add(AzureFunctionsResourceDetector())
            elif detector == Detector.GCP:
                resource_detectors.add(GoogleCloudResourceDetector())
    return list(resource_detectors)


# Example usage
detectors_string = "aws_lambda,gcp"
detectors_list = [Detector.AWS_LAMBDA, Detector.GCP]
