from typing import TYPE_CHECKING

import boto3

if TYPE_CHECKING:
    from mypy_boto3_ec2.type_defs import InstanceTypeDef


class EC2Client:
    _instances = {}

    def __new__(cls, **kwargs):
        key = tuple(sorted(kwargs.items()))
        if key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[key] = instance

        return cls._instances[key]

    def __init__(self, **kwargs):
        if not hasattr(self, "_initialized"):
            self._client = boto3.client("ec2", **kwargs)
            self._initialized = True

    def describe_instance(self, instance_id: str) -> InstanceTypeDef:
        response = self._client.describe_instances(
            InstanceIds=[instance_id],
        )
        return response["Reservations"][0]["Instances"][0]  # type: ignore

    def start_instance(self, instance_id: str):
        self._client.start_instances(
            InstanceIds=[instance_id],
        )

        waiter = self._client.get_waiter("instance_running")
        waiter.wait(InstanceIds=[instance_id])

    def stop_instance(self, instance_id: str):
        self._client.stop_instances(
            InstanceIds=[instance_id],
        )
