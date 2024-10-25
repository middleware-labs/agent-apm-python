import os
from setuptools import setup
from setuptools.command.install import install
import platform
import requests
import traceback
import yaml
import pkg_resources

# Function to send telemetry data
def send_telemetry(error_info=None):
    # Path to additional config file
    file_path = "/etc/mw-agent/agent-config.yaml"
    
    # Read file content (if any) from /etc/your-file
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                config = yaml.safe_load(file)
                token = config.get("api-key")
                url = config.get("target")
                data = {
                    "status":"apm_tried",
                    "metadata":{
                        "host_id": platform.machine(),
                        "os_type": platform.system(),
                        "apm_type":"Python",
                        "apm_data": {
                            "python_version": platform.python_version(),
                            "package_version": pkg_resources.get_distribution("middleware-apm").version,
                            "message": "installation tried",
                            "error_info": error_info,
                        },
                    },
                }
                requests.post(f"{url}/api/v1/apm/tracking/{token}", json=data)
        except Exception as e:
            pass

# Custom install command that sends telemetry data after installation
class CustomInstallCommand(install):
    def run(self):
        install.run(self)  # Call the original run method
        send_telemetry()   # Send telemetry after installation

def handle_uncaught_exception(exc_type, exc_value, exc_traceback):

    error_info = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    send_telemetry(error_info=error_info)

import sys
sys.excepthook = handle_uncaught_exception

# Setup configuration
setup(cmdclass={'install': CustomInstallCommand})
