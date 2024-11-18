import logging
import os
import requests
from opentelemetry.sdk.environment_variables import (
    OTEL_EXPORTER_OTLP_ENDPOINT,
    OTEL_LOG_LEVEL,
    OTEL_SERVICE_NAME,
)
from middleware.detectors.detector import Detector, process_detector_input
from typing import Union, List
from middleware.version import __version__
# Environment Variable Names
OTEL_SERVICE_VERSION = "OTEL_SERVICE_VERSION"
DEBUG = "DEBUG"
SAMPLE_RATE = "SAMPLE_RATE"

# Middleware Envs
MW_API_KEY = "MW_API_KEY"
MW_SERVICE_NAME = "MW_SERVICE_NAME"
MW_AGENT_SERVICE = "MW_AGENT_SERVICE"
MW_TARGET = "MW_TARGET"
MW_CUSTOM_RESOURCE_ATTRIBUTES = "MW_CUSTOM_RESOURCE_ATTRIBUTES"
MW_APM_COLLECT_TRACES = "MW_APM_COLLECT_TRACES"
MW_APM_COLLECT_METRICS = "MW_APM_COLLECT_METRICS"
MW_APM_COLLECT_LOGS = "MW_APM_COLLECT_LOGS"
MW_APM_COLLECT_PROFILING = "MW_APM_COLLECT_PROFILING"
MW_PROPAGATORS = "MW_PROPAGATORS"
MW_CONSOLE_EXPORTER = "MW_CONSOLE_EXPORTER"
MW_DEBUG_LOG_FILE = "MW_DEBUG_LOG_FILE"
MW_PROJECT_NAME = "MW_PROJECT_NAME"
MW_SAMPLE_RATE = "MW_SAMPLE_RATE"
MW_LOG_LEVEL = "MW_LOG_LEVEL"
MW_DETECTORS = "MW_DETECTORS"

OTEL_PROPAGATORS = "OTEL_PROPAGATORS"

# Default values
DEFAULT_TARGET = "http://localhost:9319"
DEFAULT_PORT = "9319"
DEFAULT_COLLECT_TRACES = True
DEFAULT_COLLECT_METRICS = True
DEFAULT_COLLECT_LOGS = True
DEFAULT_COLLECT_PROFILING = False
DEFAULT_AGENT_SERVICE = "localhost"
DEFAULT_EXPORTER_PROTOCOL = "grpc"
DEFAULT_SERVICE_NAME = f"python-service-{os.getpid()}"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_PROPAGATORS = "b3"
DEFAULT_SAMPLE_RATE = 1


# DETECTORS
DETECT_ENVVARS = Detector.ENVVARS
DETECT_AWS_LAMBDA = Detector.AWS_LAMBDA
DETECT_AWS_BEANSTALK = Detector.AWS_BEANSTALK
DETECT_AWS_ECS = Detector.AWS_ECS
DETECT_AWS_EKS = Detector.AWS_EKS
DETECT_AWS_EC2 = Detector.AWS_EC2

DETECT_AZURE_VM = Detector.AZURE_VM
DETECT_AZURE_APP_SERVICE = Detector.AZURE_APP_SERVICE
DETECT_AZURE_FUNCTIONS = Detector.AZURE_FUNCTIONS

DETECT_GCP = Detector.GCP

# Errors and Warnings
MISSING_SERVICE_NAME_ERROR = (
    "Missing service name. Specify either "
    + "OTEL_SERVICE_NAME/MW_SERVICE_NAME environment variable or service_name in the "
    + "options parameter. If left unset, this will show up in middleware "
    + "as python-service-pid"
)

log_levels = {
    "NOTSET": logging.NOTSET,
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARN": logging.WARN,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "FATAL": logging.FATAL,
    "CRITICAL": logging.CRITICAL,
}

_logger = logging.getLogger(__name__)


# pylint: disable=too-many-arguments,too-many-instance-attributes
class MWOptions:
    """
    Middleware Options used to configure the OpenTelemetry SDK.

    This class allows for the configuration of various middleware options for
    OpenTelemetry, with support for environment variables to override default
    values. If an option is set as an environment variable, it will take precedence
    over any parameter passed during instantiation. If neither is present, the
    default value will be used.

    **Attributes and Environment Variables:**

    - `access_token (str)`: API key for authentication.
      - Environment Variable: `MW_API_KEY`.
      - Example usage:
                access_token = "whkvkobudfitutobptgonaezuxpjjypnejbb"

    - `service_name (str)`: Name of the service.
      - Environment Variable: `MW_SERVICE_NAME` (alternative: `OTEL_SERVICE_NAME`).
      - Example usage:
                service_name = "MyPythonServer"

    - `collect_traces (bool)`: Flag to collect traces.
      - Environment Variable: `MW_APM_COLLECT_TRACES` (default: True).
      - Example usage:
                collect_traces = True

    - `collect_metrics (bool)`: Flag to collect metrics.
      - Environment Variable: `MW_APM_COLLECT_METRICS` (default: True).
      - Example usage:
                collect_metrics = False

    - `collect_logs (bool)`: Flag to collect logs.
      - Environment Variable: `MW_APM_COLLECT_LOGS` (default: True).
      - Example usage:
                collect_logs = True

    - `collect_profiling (bool)`: Flag to collect profiling.
      - Environment Variable: `MW_APM_COLLECT_PROFILING` (default: False).
      - Example usage:
                collect_profiling = True

    - `log_level (str)`: Logging level.
      - Environment Variable: `MW_LOG_LEVEL` (alternative: `OTEL_LOG_LEVEL`).
      - Example usage: (INFO, DEBUG, WARNING, ERROR)
                log_level = DEBUG

    - `mw_agent_service (str)`: Address of the middleware agent service.
      - Environment Variable: `MW_AGENT_SERVICE` (default: "localhost").
      - Use for containerized app with agent installed.
      - Example usage:
        (Docker)
                mw_agent_service = 172.17.0.1
        (Kubernetes)
                mw_agent_service = mw-service.mw-agent-ns.svc.cluster.local

    - `target (str)`: Target endpoint for the OTLP exporter.
      - Environment Variable: `MW_TARGET` (alternative: `OTEL_EXPORTER_OTLP_ENDPOINT`, default: "http://localhost:9319").
      - Use Target for Agent-less setup i.e agent is not installed.
      - Example usage:
                target = "https://myapp.middleware.io:443"

    - `custom_resource_attributes (str)`: Custom resource attributes.
      - Environment Variable: `MW_CUSTOM_RESOURCE_ATTRIBUTES`.
      - Example usage:
                custom_resource_attributes = "call_id=12345678, request_id=987654321"


    - `otel_propagators (str)`: Propagators for context propagation.
      - Environment Variable: `MW_PROPAGATORS` (alternative: `OTEL_PROPAGATORS`, default: "b3").
      - Example usage:(https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/#:~:text=Known%20values%20for%20OTEL_PROPAGATORS%20are%3A)
                otel_propagators = "b3,tracecontext"

    - `console_exporter (bool)`: Flag to enable console exporter.It dumps telemetry data to console.
      - Environment Variable: `MW_CONSOLE_EXPORTER` (default: False).
      - Example usage:
                console_exporter = True

    - `debug_log_file (bool)`: Flag to enable debug logging to file. To dump telemetry data in files.
      - Environment Variable: `MW_DEBUG_LOG_FILE` (default: False).
      - Use only if console_exporter is used.
      - Example usage:
                debug_log_file = True

    - `project_name (str)`: Name of the project.
      - Environment Variable: `MW_PROJECT_NAME`.
      - Example usage:
                project_name = "TestingProject"

    - `sample_rate (int)`: Sample rate for telemetry data.
      - Environment Variable: `MW_SAMPLE_RATE`.
      - Should be the value from `0` to `1`.
        AlwaysOn (1), AlwaysOff (0), or a TraceIdRatio as 1/N
      - To use OTEL Sampler use ENVs and avoid this sample_rate.
      - Example usage:
                sample_rate = 0.5

    - `detectors (str,List[Detector])`: Detectors to add for aws, azure, gcp or envvars.
      - Environment Variable: `MW_DETECTORS`.
      - Example usage:
                detectors_string = "aws_lambda,gcp" for MW_DETECTORS
                detectors_list = [DETECT_AWS_LAMBDA, DETECT_GCP]

    **Defaults**:

    - Target: http://localhost:9319
    - Log Level: INFO
    - Collect Traces: True
    - Collect Metrics: True
    - Collect Logs: True
    - Agent Service: 'localhost'
    - Agent Service: 'localhost'
    - Service Name: 'unknown_service:python'
    - Propagators: 'b3'
    - Sample Rate: 1

    """

    access_token = None
    service_name = None
    collect_traces = DEFAULT_COLLECT_TRACES
    collect_metrics = DEFAULT_COLLECT_METRICS
    collect_logs = DEFAULT_COLLECT_LOGS
    collect_profiling = DEFAULT_COLLECT_PROFILING
    log_level = DEFAULT_LOG_LEVEL
    mw_agent_service = DEFAULT_AGENT_SERVICE
    target = DEFAULT_TARGET
    custom_resource_attributes = None
    otel_propagators = DEFAULT_PROPAGATORS
    console_exporter = False
    debug_log_file = False
    project_name = None
    sample_rate = None
    detectors = None

    def __init__(
        self,
        access_token: str = None,
        service_name: str = None,
        collect_traces: bool = DEFAULT_COLLECT_TRACES,
        collect_metrics: bool = DEFAULT_COLLECT_METRICS,
        collect_logs: bool = DEFAULT_COLLECT_LOGS,
        collect_profiling: bool = DEFAULT_COLLECT_PROFILING,
        log_level: str = DEFAULT_LOG_LEVEL,
        mw_agent_service: str = DEFAULT_AGENT_SERVICE,
        target: str = DEFAULT_TARGET,
        custom_resource_attributes: str = None,
        otel_propagators: str = DEFAULT_PROPAGATORS,
        console_exporter: bool = False,
        debug_log_file: bool = False,
        project_name: str = None,
        sample_rate: int = None,
        detectors: Union[str, List[Detector]] = None,
    ):
        self.access_token = os.environ.get(MW_API_KEY, access_token)
        self.service_name = os.environ.get(
            OTEL_SERVICE_NAME, os.environ.get(MW_SERVICE_NAME, service_name)
        )
        if not self.service_name:
            _logger.debug(MISSING_SERVICE_NAME_ERROR)
            self.service_name = DEFAULT_SERVICE_NAME

        self.collect_traces = parse_bool(MW_APM_COLLECT_TRACES, collect_traces)
        self.collect_metrics = parse_bool(MW_APM_COLLECT_METRICS, collect_metrics)
        self.collect_logs = parse_bool(MW_APM_COLLECT_LOGS, collect_logs)
        self.collect_profiling = parse_bool(MW_APM_COLLECT_PROFILING, collect_profiling)

        log_level = os.environ.get(
            OTEL_LOG_LEVEL, os.environ.get(MW_LOG_LEVEL, log_level)
        )
        if log_level and log_level.upper() in log_levels:
            self.log_level = log_level.upper()
            logging.basicConfig(level=log_levels[self.log_level])
        else:
            _logger.warning("invalid log_level:", log_level)

        self.target = os.environ.get(
            OTEL_EXPORTER_OTLP_ENDPOINT, os.environ.get(MW_TARGET, target)
        )

        if "https" not in self.target:
            self.mw_agent_service = os.environ.get(MW_AGENT_SERVICE, mw_agent_service)
            if self.mw_agent_service is not None:
                self.target = f"http://{self.mw_agent_service}:{DEFAULT_PORT}"

        self.custom_resource_attributes = os.environ.get(
            MW_CUSTOM_RESOURCE_ATTRIBUTES, custom_resource_attributes
        )

        self.otel_propagators = os.environ.get(
            OTEL_PROPAGATORS, os.environ.get(MW_PROPAGATORS, otel_propagators)
        )
        os.environ["OTEL_PROPAGATORS"] = self.otel_propagators    
        self.console_exporter = parse_bool(MW_CONSOLE_EXPORTER, console_exporter)
        self.debug_log_file = parse_bool(MW_DEBUG_LOG_FILE, debug_log_file)
        self.project_name = os.environ.get(MW_PROJECT_NAME, project_name)
        self.sample_rate = parse_int(MW_SAMPLE_RATE, sample_rate, DEFAULT_SAMPLE_RATE)
        self.detectors = os.environ.get(MW_DETECTORS, detectors)
        _health_check(options=self)
        _get_instrument_info(options=self)

def parse_bool(
    environment_variable: str, default_value: bool, error_message: str = None
) -> bool:
    """
    Attempts to parse the provided environment variable into a bool. If it
    does not exist or fails parse, the default value is returned instead.

    Args:
        environment_variable (str): the environment variable name to use
        default_value (bool): the default value if not found or unable parse
        error_message (str): the error message to log if unable to parse

    Returns:
        bool: either the parsed environment variable or default value
    """
    val = os.getenv(environment_variable, None)
    if val:
        try:
            if val.upper() == "FALSE":
                return False
            if val.upper() == "TRUE":
                return True
            return False
        except ValueError:
            if error_message is not None:
                _logger.warning(error_message)
    return default_value


def parse_int(
    environment_variable: str, param: int, default_value: int, error_message: str = None
) -> int:
    """
    Attempts to parse the provided environment variable into an int. If it
    does not exist or fails parse, the default value is returned instead.

    Args:
        environment_variable (str): the environment variable name to use
        param(int): fallback parameter to check before setting default
        default_value (int): the default value if not found or unable parse
        error_message (str): the error message to log if unable to parse

    Returns:
        int: either the parsed environment variable, param, or default value
    """
    val = os.getenv(environment_variable, None)
    if val:
        try:
            return int(val)
        except ValueError:
            if error_message is not None:
                _logger.warning(error_message)
            return default_value
    elif isinstance(param, int):
        return param
    else:
        return default_value

def _health_check(options: MWOptions):
    if options.target == "" or ("https" not in options.target) :
        try:
            response = requests.get(
                f"http://{options.mw_agent_service}:13133/healthcheck", timeout=5
            )
            if response.status_code != 200:
                _logger.warning(
                    "MW Agent Health Check is failing ...\nThis could be due to incorrect value of MW_AGENT_SERVICE\nIgnore the warning if you are using MW Agent older than 1.7.7 (You can confirm by running `mw-agent version`)"
                )
        except requests.exceptions.RequestException as e:
            _logger.warning(f"MW Agent Health Check is failing ...\nException while MW Agent Health Check:{e}")

def _get_instrument_info(options: MWOptions):
    _logger.debug(
        f"Middleware Python Instrumentation Started with SDK version: {__version__}"
    )
    if options.target == "" or ("https" not in options.target):
        _logger.debug(f"Using Agent Instrumentation")
    else:
        _logger.debug(f"Using Serverless Instrumentation")
    _logger.debug(f"OTLP Endpoint:{options.target}")
    if options.collect_metrics:
        _logger.debug(f"Metrics: Enabled")
    if options.collect_traces:
        _logger.debug(f"Traces: Enabled")
    if options.collect_logs:
        _logger.debug(f"Logs: Enabled")
    if options.collect_profiling:
        _logger.debug(f"Profiling: Enabled")
