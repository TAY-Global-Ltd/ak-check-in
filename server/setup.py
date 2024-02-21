from aws_setup.create_lambda import create_lambda_func
from aws_setup.create_api_gateway import create_all as create_api_gateway

if __name__ == '__main__':
    stage = 'uat'
    create_lambda_func(stage)
    create_api_gateway(stage)
