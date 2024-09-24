import subprocess
import pkg_resources
import sys

# This command scans the list of packages currently present in your active 'site-packages' directory
# and automatically deploys the relevant instrumentation libraries associated with these packages, if applicable.
#
# For instance, if you have previously installed the 'flask' package,
# this command will install 'opentelemetry-instrumentation-flask' on your behalf.
def _pip_install(package):
    # explicit upgrade strategy to override potential pip config
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-U",
            "--upgrade-strategy",
            "only-if-needed",
            package,
        ]
    )

def _bootstrap():

    cmd = "middleware-bootstrap"

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        output = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running init middleware-bootstrap: {e}")
        output = ""

    libraries = output.splitlines()

    for library in libraries:
        library_name, library_version = library.split("==", 1)

        try:
            installed_version = pkg_resources.get_distribution(library_name).version
            if installed_version != library_version:
                # The library is not updated, so update it
                try:
                    _pip_install(library)
                    # subprocess.run(["pip", "uninstall", "-y", library_name], check=True)
                    # subprocess.run(["pip", "install", library], check=True)
                    print(f"{library_name} has been updated to version {library_version}.")
                except subprocess.CalledProcessError as e:
                    print(f"Error updating {library_name} to version {library_version}: {e}")

        except pkg_resources.DistributionNotFound:
            # The library is not installed, so install it
            try:
                _pip_install(library)
                # subprocess.run(["pip", "install", library], check=True)
                print(f"{library} has been installed.")
            except subprocess.CalledProcessError as e:
                print(f"Error installing {library}: {e}")

    print("Bootstrapping is done, Relevant instrumentation libraries associated with existing packages. \n")