import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from salome.utils.aws import EC2Client

if TYPE_CHECKING:
    from salome.bot import SalomeBot


class MinecraftActionHandler(ABC):
    def __init__(self, bot: SalomeBot):
        self.bot = bot

    def require_stopped(self, message) -> bool:
        instance_id = os.environ["MINECRAFT_INSTANCE_ID"]
        instance_region = os.environ.get("MINECRAFT_INSTANCE_REGION", "ap-south-1")

        ec2 = EC2Client(region_name=instance_region)
        instance = ec2.describe_instance(instance_id)

        if instance["State"]["Name"] != "stopped":  # type: ignore
            self.bot.client.send_followup_message(
                interaction_token=message["token"],
                content=(
                    "あら?インスタンスが「停止済み」ではないみたいですわ...\n"
                    "インスタンスの状態を確認してくださる?"
                ),
            )
            return False
        return True

    def require_running(self, message) -> bool:
        instance_id = os.environ["MINECRAFT_INSTANCE_ID"]
        instance_region = os.environ.get("MINECRAFT_INSTANCE_REGION", "ap-south-1")

        ec2 = EC2Client(region_name=instance_region)
        instance = ec2.describe_instance(instance_id)

        if instance["State"]["Name"] != "running":  # type: ignore
            self.bot.client.send_followup_message(
                interaction_token=message["token"],
                content=(
                    "あら?インスタンスが「実行中」ではないみたいですわ...\n"
                    "インスタンスの状態を確認してくださる?"
                ),
            )
            return False
        return True

    @abstractmethod
    def __call__(self, message):
        raise NotImplementedError
