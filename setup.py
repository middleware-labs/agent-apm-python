import setuptools

try:
    with open("requirements.txt", "r") as f:
        requirements = f.read().splitlines()
except IOError:
    requirements = []


setuptools.setup(

    name="middleware-apm",
    version="0.2.1",
    install_requires=requirements,
    author="middleware-dev",
    description="Middleware's APM tool enables Python developers to effortlessly monitor their applications, gathering distributed tracing, metrics, logs, and profiling data for valuable insights and performance optimization. Install the Middleware Host agent and integrate the APM package to leverage its powerful functionalities.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=["mw_tracker"],
    url = "https://github.com/middleware-labs/agent-apm-python.git",
    entry_points={
        'console_scripts': [
            'middleware-instrument = opentelemetry.instrumentation.auto_instrumentation:run',
            'middleware-bootstrap = opentelemetry.instrumentation.bootstrap:run',
        ],
    },
)