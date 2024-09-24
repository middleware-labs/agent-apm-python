import subprocess
import os
import shutil
import pkg_resources
from middleware.config import config
from importlib.resources import files
from middleware.installer import command
from middleware.installer._bootstrap import _bootstrap

CONFIG_FILE_PATH = os.getenv('MIDDLEWARE_CONFIG_FILE', os.path.join(os.getcwd(), "middleware.ini"))
DEFAULT_CONFIG_FILE_PATH = pkg_resources.resource_filename('middleware', 'middleware.ini')


def copy_default_config():
    """
    Copies the default configuration file if it doesn't exist in the target location.
    """
    if not os.path.exists(CONFIG_FILE_PATH):
        try:
            shutil.copy(DEFAULT_CONFIG_FILE_PATH, CONFIG_FILE_PATH)
            print(f"Generated default config file: {CONFIG_FILE_PATH}")
        except Exception as e:
            print(f"Failed to generate default config file:{e}")


@command('init', 'Initialize the default configuration',
         """Creates a default configuration file if it doesn't exist in the specified location.
         
         The config file path can be set using the environment variable MIDDLEWARE_CONFIG_FILE, 
         otherwise, it defaults to 'middleware.ini'.""")

def init(args):
    """
    Command to initialize the default configuration.
    """
    copy_default_config()
    _bootstrap()

    
@command('run', '...',
         """Executes the command line but forces the initialization of the agent
         automatically at startup.

         If using an agent configuration file, the path to the file should be
         supplied by the environment variable MIDDLEWARE_CONFIG_FILE.""")
def run(args):
    if len(args) == 0:
        print("Expected args are missing.")
        return

    exporters = [
        "--traces_exporter otlp" if config.collect_traces else "--traces_exporter none",
        "--metrics_exporter otlp" if config.collect_metrics else "--metrics_exporter none",
        "--logs_exporter otlp" if config.collect_logs else "--logs_exporter none"
    ]

    # cmd1 = "middleware-bootstrap -a install"
    cmd2 = f"middleware-instrument {' '.join(exporters)} \
    --tracer_provider sdk_tracer_provider \
    --exporter_otlp_endpoint {config.exporter_otlp_endpoint} \
    --resource_attributes {config.resource_attributes} \
    --service_name {config.service_name} \
    --propagators {config.otel_propagators} {' '.join(args)}"

    # try:
    #     subprocess.run(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
    # except subprocess.CalledProcessError as e:
    #     print(f"Failed bootstrapping with error: {e}")

    _bootstrap()

    try:
        subprocess.run(cmd2, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed instrumenting with error: {e}")
