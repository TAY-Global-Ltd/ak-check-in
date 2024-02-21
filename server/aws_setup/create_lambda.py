import boto3
from settings import AWS_REGION, LAMBDA_FUNCTION_MAP, ROLE_NAME, AWS_ACCOUNT

lambda_client = boto3.client("lambda", region_name=AWS_REGION)


def create_lambda_func(stage):
    func_name = LAMBDA_FUNCTION_MAP[stage]

    with open("dummy_lambda.zip", "rb") as f:
        zipped_code = f.read()

    response = lambda_client.create_function(
        FunctionName=func_name,
        Runtime="python3.12",
        Role=f"arn:aws:iam::{AWS_ACCOUNT}:role/{ROLE_NAME}",
        Handler="lambda_function.lambda_handler",  # replace with your handler
        Code=dict(ZipFile=zipped_code),
        Timeout=30,  # Timeout in seconds
        MemorySize=128,  # Minimum memory size in MB
    )

    print(response)
