import boto3
from settings import AWS_REGION, API_GATEWAY_MAP, LAMBDA_FUNCTION_MAP, ROLE_NAME

client = boto3.client("apigateway", region_name=AWS_REGION)

RESOURCE_NAMES = "current_event", "next_event", "initial_state"


def get_rest_api_id(stage):
    response = client.get_rest_apis()
    name = API_GATEWAY_MAP[stage]
    return next(x["id"] for x in response["items"] if x["name"] == name)


def _get_resource_id(rest_api_id, path):
    response = client.get_resources(restApiId=rest_api_id)
    if not path.startswith("/"):
        path = "/" + path

    return next(x["id"] for x in response["items"] if x["path"] == path)


def create_resources(rest_api_id):
    for name in RESOURCE_NAMES:
        create_resource(rest_api_id, name)


def create_resource(rest_api_id, path_part):
    root_id = _get_resource_id(rest_api_id, "/")

    response = client.create_resource(
        restApiId=rest_api_id,
        parentId=root_id,
        pathPart=path_part,
    )

    print(response)


def create_method(rest_api_id, resource_id):
    response = client.put_method(
        restApiId=rest_api_id,
        resourceId=resource_id,
        httpMethod="GET",
        authorizationType="NONE",
    )

    print(response)


def get_role_arn():
    iam = boto3.client("iam")

    response = iam.get_role(RoleName=ROLE_NAME)

    return response["Role"]["Arn"]


def create_integration(stage, rest_api_id, resource_id):
    lambda_uri = get_lambda_function_uri(LAMBDA_FUNCTION_MAP[stage])
    uri = f"arn:aws:apigateway:{AWS_REGION}:lambda:path/2015-03-31/functions/{lambda_uri}/invocations"
    print(uri)

    credentials = get_role_arn()

    response = client.put_integration(
        restApiId=rest_api_id,
        resourceId=resource_id,
        httpMethod="GET",
        type="AWS_PROXY",
        integrationHttpMethod="POST",
        uri=uri,
        credentials=credentials,
    )

    print(response)


def get_lambda_function_uri(function_name):
    client = boto3.client("lambda", region_name=AWS_REGION)
    response = client.get_function(FunctionName=function_name)
    return response["Configuration"]["FunctionArn"]


def create_deploy(rest_api_id, stage):
    response = client.create_deployment(
        restApiId=rest_api_id,
        stageName=stage,  # replace with your stage name
        description=f"{stage} stage",
    )

    print(response)


def create_api_gateway(stage):
    response = client.create_rest_api(
        name=API_GATEWAY_MAP[stage],
        description="An API gateway to server ak-check-in",
        endpointConfiguration={
            "types": [
                "REGIONAL",
            ]
        },
    )

    print(response)


def get_deployed_url(stage, rest_api_id):
    url = f"https://{rest_api_id}.execute-api.{AWS_REGION}.amazonaws.com/{stage}"
    return url


def create_methods(stage, rest_api_id):
    for name in RESOURCE_NAMES:
        resource_id = _get_resource_id(rest_api_id, name)
        create_method(rest_api_id, resource_id)
        create_integration(stage, rest_api_id, resource_id)


def create_all(stage):
    create_api_gateway(stage)
    rest_api_id = get_rest_api_id(stage)
    create_resources(rest_api_id)
    create_methods(stage, rest_api_id)

    create_deploy(rest_api_id, stage)
    url = get_deployed_url(stage, rest_api_id)
    print(f"Base URL is: {url}")
