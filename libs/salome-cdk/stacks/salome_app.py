import os

import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_bedrock_alpha as bedrock
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as sns_subscriptions
from constructs import Construct
from salome.config import Config

DISCORD_APPLICATION_ID = os.environ["DISCORD_APPLICATION_ID"]
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
DISCORD_PUBLIC_KEY = os.environ["DISCORD_PUBLIC_KEY"]


class SalomeAppStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # 🐧 Bedrock Foundation Models 🐧

        salome_foundation_model = bedrock.BedrockFoundationModel(
            value=Config.DEFAULT_MODEL_ID
        )

        # 🐧 SNS Topics 🐧

        salome_server_interact_topic = sns.Topic(
            self,
            "SalomeServerInteractTopic",
            topic_name="salome-server-interact-topic",
        )

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
            role_name="salome-function-role",
        )
        salome_foundation_model.grant_invoke(salome_function_role)
        salome_server_interact_topic.grant_publish(salome_function_role)

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
            environment={
                "DISCORD_PUBLIC_KEY": DISCORD_PUBLIC_KEY,
                "SERVER_INTERACT_TOPIC_ARN": salome_server_interact_topic.topic_arn,
            },
        )

        salome_server_interact_ask_function = _lambda.DockerImageFunction(
            self,
            "SalomeServerInteractAskFunction",
            code=_lambda.DockerImageCode.from_image_asset(
                directory="../..",
                cmd=["functions.server.interact.ask.function.handler"],
            ),
            architecture=_lambda.Architecture.ARM_64,
            function_name="salome-server-interact-ask-function",
            role=salome_function_role,  # type: ignore
            timeout=cdk.Duration.minutes(5),
            environment={
                "DISCORD_APPLICATION_ID": DISCORD_APPLICATION_ID,
                "DISCORD_BOT_TOKEN": DISCORD_BOT_TOKEN,
            },
        )
        salome_server_interact_topic.add_subscription(
            sns_subscriptions.LambdaSubscription(
                salome_server_interact_ask_function,  # type: ignore
                filter_policy={
                    "command": sns.SubscriptionFilter.string_filter(
                        allowlist=["ask"],
                    ),
                },
            )
        )

        # 🐧 API Gateway & Integration 🐧

        salome_api = apigw.LambdaRestApi(
            self,
            "SalomeApi",
            handler=salome_api_function,  # type: ignore
            deploy_options=apigw.StageOptions(stage_name="v1"),
            rest_api_name="salome-api",
        )
