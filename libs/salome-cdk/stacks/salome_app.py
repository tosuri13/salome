import os

import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3vectors as s3vectors
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as sns_subscriptions
from constructs import Construct
from salome.config import Config

DISCORD_APPLICATION_ID = os.environ["DISCORD_APPLICATION_ID"]
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
DISCORD_PUBLIC_KEY = os.environ["DISCORD_PUBLIC_KEY"]

MINECRAFT_SERVER_INSTANCE_ID = os.environ["MINECRAFT_SERVER_INSTANCE_ID"]
MINECRAFT_SERVER_INSTANCE_REGION = os.environ["MINECRAFT_SERVER_INSTANCE_REGION"]
MINECRAFT_SERVER_WORLD_NAME = os.environ["MINECRAFT_SERVER_WORLD_NAME"]


class SalomeAppStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # 🐧 S3 Buckets 🐧

        salome_minecraft_backup_bucket = s3.Bucket(
            self,
            "SalomeMinecraftBackupBucket",
            bucket_name="salome-minecraft-backup-bucket",
        )

        # 🐧 S3 Vectors & Indexes 🐧

        salome_recipe_vector_bucket = s3vectors.CfnVectorBucket(
            self,
            "SalomeRecipeVectorBucket",
            vector_bucket_name="salome-recipe-vector-bucket",
        )

        salome_recipes_vector_index = s3vectors.CfnIndex(
            self,
            "SalomeRecipesVectorIndex",
            data_type="float32",
            dimension=Config.DEFAULT_EMBEDDING_DIMENSIONS,
            distance_metric="cosine",
            index_name="recipes",
            metadata_configuration=s3vectors.CfnIndex.MetadataConfigurationProperty(
                non_filterable_metadata_keys=["text"]
            ),
            vector_bucket_arn=salome_recipe_vector_bucket.attr_vector_bucket_arn,
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
            inline_policies={
                "salome-function-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "bedrock:InvokeModel",
                                "bedrock:InvokeModelWithResponseStream",
                                "ec2:DescribeInstances",
                                "ec2:StartInstances",
                                "ec2:StopInstances",
                                "s3Vectors:DeleteVectors",
                                "s3Vectors:GetVectors",
                                "s3Vectors:ListVectors",
                                "s3Vectors:PutVectors",
                                "s3Vectors:QueryVectors",
                                "sns:Publish",
                                "ssm:GetCommandInvocation",
                                "ssm:SendCommand",
                            ],
                            effect=iam.Effect.ALLOW,
                            resources=["*"],
                        ),
                    ]
                )
            },
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole",
                )
            ],
            role_name="salome-function-role",
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

        salome_server_interact_minecraft_function = _lambda.DockerImageFunction(
            self,
            "SalomeServerInteractMinecraftFunction",
            code=_lambda.DockerImageCode.from_image_asset(
                directory="../..",
                cmd=["functions.server.interact.minecraft.function.handler"],
            ),
            architecture=_lambda.Architecture.ARM_64,
            function_name="salome-server-interact-minecraft-function",
            role=salome_function_role,  # type: ignore
            timeout=cdk.Duration.minutes(5),
            environment={
                "DISCORD_APPLICATION_ID": DISCORD_APPLICATION_ID,
                "DISCORD_BOT_TOKEN": DISCORD_BOT_TOKEN,
                "MINECRAFT_SERVER_INSTANCE_ID": MINECRAFT_SERVER_INSTANCE_ID,
                "MINECRAFT_SERVER_INSTANCE_REGION": MINECRAFT_SERVER_INSTANCE_REGION,
                "MINECRAFT_SERVER_WORLD_NAME": MINECRAFT_SERVER_WORLD_NAME,
                "MINECRAFT_BACKUP_BUCKET_NAME": salome_minecraft_backup_bucket.bucket_name,
            },
        )
        salome_server_interact_topic.add_subscription(
            sns_subscriptions.LambdaSubscription(
                salome_server_interact_minecraft_function,  # type: ignore
                filter_policy={
                    "command": sns.SubscriptionFilter.string_filter(
                        allowlist=["minecraft"],
                    ),
                },
            )
        )

        salome_server_interact_recipe_function = _lambda.DockerImageFunction(
            self,
            "SalomeServerInteractRecipeFunction",
            code=_lambda.DockerImageCode.from_image_asset(
                directory="../..",
                cmd=["functions.server.interact.recipe.function.handler"],
            ),
            architecture=_lambda.Architecture.ARM_64,
            function_name="salome-server-interact-recipe-function",
            role=salome_function_role,  # type: ignore
            timeout=cdk.Duration.minutes(5),
            environment={
                "DISCORD_APPLICATION_ID": DISCORD_APPLICATION_ID,
                "DISCORD_BOT_TOKEN": DISCORD_BOT_TOKEN,
                "RECIPE_VECTOR_INDEX_ARN": salome_recipes_vector_index.attr_index_arn,
            },
        )
        salome_server_interact_topic.add_subscription(
            sns_subscriptions.LambdaSubscription(
                salome_server_interact_recipe_function,  # type: ignore
                filter_policy={
                    "command": sns.SubscriptionFilter.string_filter(
                        allowlist=["recipe"],
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
