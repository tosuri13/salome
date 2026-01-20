from typing import TYPE_CHECKING, Mapping

import boto3

if TYPE_CHECKING:
    from mypy_boto3_sns.type_defs import MessageAttributeValueTypeDef


class SNSClient:
    _instances = {}

    def __new__(cls, **kwargs):
        key = tuple(sorted(kwargs.items()))
        if key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[key] = instance

        return cls._instances[key]

    def __init__(self, **kwargs):
        if not hasattr(self, "_initialized"):
            self._client = boto3.client("sns", **kwargs)
            self._initialized = True

    def publish(
        self,
        topic_arn: str,
        message: str,
        message_attributes: Mapping[str, MessageAttributeValueTypeDef],
    ):
        self._client.publish(
            TopicArn=topic_arn,
            Message=message,
            MessageAttributes=message_attributes,
        )
