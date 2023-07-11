import setuptools

try:
    with open("requirements.txt", "r") as f:
        requirements = f.read().splitlines()
except IOError:
    requirements = []


setuptools.setup(

    name="middleware-apm",
    version="0.1.42rc3",
    install_requires=requirements,
    author="middleware-dev",
    description="This package is use to check the RAM and CPU Usage of Current Device.",
    long_description=open('README.md').read(),
    long_description_content_type='text/plain',
    packages=["apmpythonpackage"],
    url = "https://github.com/middleware-labs/agent-apm-python.git",
    entry_points={
        'console_scripts': [
            'middleware-instrument = opentelemetry.instrumentation.auto_instrumentation:run',
            'middleware-bootstrap = opentelemetry.instrumentation.bootstrap:run',
        ],
    },
)
