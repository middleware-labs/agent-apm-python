import sys
import setuptools

python_version = sys.version_info[:2]
assert python_version >= (3,8,), "Middleware APM supports: Python 3.8+"

try:
    with open("requirements.txt", "r") as f:
        requirements = f.read().splitlines()
except IOError:
    requirements = []

packages = [
    "scripts",
    "middleware",
    "middleware.installer",
    "middleware.lib",
]

setuptools.setup(
    name="middleware-apm",
    version="1.1.0",
    install_requires=requirements,
    author="middleware-dev",
    maintainer="middleware-dev",
    license="Apache-2.0",
    description="Middleware's APM tool enables Python developers to effortlessly monitor their applications, gathering distributed tracing, metrics, logs, and profiling data for valuable insights and performance optimization. Install the Middleware Host agent and integrate the APM package to leverage its powerful functionalities.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=packages,
    python_requires=">=3.8",
    url = "https://docs.middleware.io/docs/apm-configuration/python",
    project_urls={"Source": "https://github.com/middleware-labs/agent-apm-python.git"},
    entry_points={
        'console_scripts': [
            'middleware-apm = middleware.installer:main',
            'middleware-instrument = opentelemetry.instrumentation.auto_instrumentation:run',
            'middleware-bootstrap = opentelemetry.instrumentation.bootstrap:run',
        ],
    },
)