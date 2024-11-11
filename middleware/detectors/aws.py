import os
import requests

def is_running_on_aws_lambda():
    return 'AWS_EXECUTION_ENV' in os.environ

def is_running_on_aws_beanstalk():
    # Elastic Beanstalk adds an environment variable for the application
    return 'AWS_ELASTIC_BEANSTALK' in os.environ

def is_running_on_aws_ec2():
    # EC2 instances can access instance metadata at the following URL
    try:
        response = requests.get('http://169.254.169.254/latest/meta-data/', timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

def is_running_on_aws_ecs():
    # ECS tasks can access ECS metadata via the metadata service
    ecs_metadata_url = 'http://169.254.170.2/v2/metadata'
    try:
        response = requests.get(ecs_metadata_url, timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

def is_running_on_aws_eks():
    # EKS clusters expose a specific environment variable
    return 'KUBERNETES_SERVICE_HOST' in os.environ

def get_aws_environment():
    if is_running_on_aws_lambda():
        return "LF"
    elif is_running_on_aws_beanstalk():
        return "BS"
    elif is_running_on_aws_ecs():
        return "ECS"
    elif is_running_on_aws_eks():
        return "EKS"
    elif is_running_on_aws_ec2():
        return "EC2"
    else:
        return "NA"

