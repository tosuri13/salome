from typing import TYPE_CHECKING, Any

import boto3

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.type_defs import QueryOutputTypeDef


class DynamoDBClient:
    _instances = {}

    def __new__(cls, **kwargs):
        key = tuple(sorted(kwargs.items()))
        if key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[key] = instance

        return cls._instances[key]

    def __init__(self, **kwargs):
        if not hasattr(self, "_initialized"):
            self._client = boto3.client("dynamodb", **kwargs)
            self._initialized = True

    def query(self, **kwargs: Any) -> QueryOutputTypeDef:
        return self._client.query(**kwargs)
