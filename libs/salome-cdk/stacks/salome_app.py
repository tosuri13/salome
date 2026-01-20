import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class SalomeAppStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # 🐧 IAM Roles 🐧

        salome_function_role = iam.Role(
            self,
            "SalomeFunctionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),  # type: ignore
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole",
                )
            ],
        )

        # 🐧 Lambda Functions 🐧

        salome_api_function = _lambda.DockerImageFunction(
            self,
            "SalomeApiFunction",
            code=_lambda.DockerImageCode.from_image_asset(
                directory="../..",
                cmd=["functions.api.function.handler"],
            ),
            architecture=_lambda.Architecture.ARM_64,
            function_name="salome-api-function",
            role=salome_function_role,  # type: ignore
            timeout=cdk.Duration.minutes(5),
        )

        # 🐧 API Gateway & Integration 🐧

        salome_api = apigw.LambdaRestApi(
            self,
            "SalomeApi",
            handler=salome_api_function,  # type: ignore
            deploy_options=apigw.StageOptions(stage_name="v1"),
            rest_api_name="salome-api",
        )
