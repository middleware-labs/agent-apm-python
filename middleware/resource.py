from logging import getLogger
from opentelemetry.sdk.resources import (
    Resource,
    ResourceDetector,
    ProcessResourceDetector,
    OTELResourceDetector,
    OsResourceDetector,
    get_aggregated_resources,
)
from opentelemetry_resourcedetector_docker import DockerResourceDetector
from middleware.options import MWOptions
from middleware.detectors.detector import process_detector_input, get_detectors
from middleware.version import __version__
import typing

_logger = getLogger(__name__)


def create_resource(options: MWOptions):
    """
    Configures and returns a new OpenTelemetry Resource.

    Args:
        options (MWOptions): the middleware options to configure with
        resource (Resource): the resource to use with the new resource

    Returns:
        Resource: the new Resource
    """
    attributes = {
        "service.name": options.service_name,
        "mw.sdk.version": __version__,
        "mw.app.lang": "python",
        "runtime.metrics.python": "true",
    }
    if "https" in options.target:
        attributes["mw.serverless"] = "true"
    if options.access_token is not None:
        attributes["mw.account_key"] = options.access_token
    if options.project_name is not None:
        attributes["project.name"] = options.project_name
    if options.custom_resource_attributes is not None:
        try:
            extra = {
                k.strip(): v.strip()
                for k, v in (
                    item.split("=")
                    for item in options.custom_resource_attributes.split(",")
                )
            }
            attributes.update(extra)
        except Exception as exc:
            _logger.warning(
                "Skipped Custom attributes: parsing error expected format `abcd=1234,wxyz=5678`"
            )

    detectors: typing.List["ResourceDetector"] = [
        OTELResourceDetector(),
        ProcessResourceDetector(),
        OsResourceDetector(),
        DockerResourceDetector(),
    ]

    if options.detectors is not None:
        extra_detectors = get_detectors(process_detector_input(options.detectors))
        if extra_detectors is not None and len(extra_detectors) > 0:
            detectors.extend(extra_detectors)
    resources = get_aggregated_resources(
        detectors,
        initial_resource=Resource.create(attributes),
    )
    return resources
