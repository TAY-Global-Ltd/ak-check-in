from aws_setup.create_lambda import create_lambda_func
from aws_setup.create_api_gateway import create_all as create_api_gateway

if __name__ == '__main__':
    stages = ['uat', 'prod']
    for stage in stages:
        print('-' * 80)
        print(f"Setting up: {stage}")
        print('-' * 80)
        create_lambda_func(stage)
        create_api_gateway(stage)

