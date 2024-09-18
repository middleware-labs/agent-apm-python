import sys
import pkg_resources

# Python APM SDK version
SDK_VERSION = pkg_resources.get_distribution("middleware-apm").version

# Define constants for Python version and SDK version
PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
