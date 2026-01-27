import time
from typing import TYPE_CHECKING

import boto3

if TYPE_CHECKING:
    from mypy_boto3_ssm.type_defs import GetCommandInvocationResultTypeDef


class SSMClient:
    _instances = {}

    def __new__(cls, **kwargs):
        key = tuple(sorted(kwargs.items()))
        if key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[key] = instance

        return cls._instances[key]

    def __init__(self, **kwargs):
        if not hasattr(self, "_initialized"):
            self._client = boto3.client("ssm", **kwargs)
            self._initialized = True

    def send_command(
        self,
        instance_id: str,
        commands: list[str],
        timeout_seconds: int = 60,
    ) -> str:
        response = self._client.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={
                "commands": commands,
            },
            TimeoutSeconds=timeout_seconds,
        )
        return response["Command"]["CommandId"]  # type: ignore

    def wait_for_command(
        self,
        command_id: str,
        instance_id: str,
        interval: float = 5.0,
        max_attempts: int = 24,
    ) -> GetCommandInvocationResultTypeDef:
        for _ in range(max_attempts):
            response = self._client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id,
            )
            status = response["Status"]

            if status in ("Success", "Failed", "Cancelled", "TimedOut"):
                return response

            time.sleep(interval)

        raise TimeoutError(
            f"SSM command timed out after {max_attempts * interval}s",
        )
