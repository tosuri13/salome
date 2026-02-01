import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from salome.config import Config
from salome.utils.aws import EC2Client

if TYPE_CHECKING:
    from salome.bot import SalomeBot


class MinecraftActionHandler(ABC):
    def __init__(self, bot: SalomeBot):
        self.bot = bot

        self.instance_id = os.environ["MINECRAFT_SERVER_INSTANCE_ID"]
        self.instance_region = os.environ["MINECRAFT_SERVER_INSTANCE_REGION"]

        self.ec2 = EC2Client(region_name=self.instance_region)

    def is_server_stopped(self, message: dict[str, Any]) -> bool:
        instance = self.ec2.describe_instance(self.instance_id)

        if instance["State"]["Name"] != "stopped":  # type: ignore
            self.bot.client.send_followup_message(
                interaction_token=message["token"],
                embeds=[
                    {
                        "description": (
                            "あら?インスタンスが「停止済み」ではないみたいですわ...\n"
                            "インスタンスの状態を確認してくださる?"
                        ),
                        "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                    }
                ],
            )
            return False
        else:
            return True

    def is_server_running(self, message: dict[str, Any]) -> bool:
        instance = self.ec2.describe_instance(self.instance_id)

        if instance["State"]["Name"] != "running":  # type: ignore
            self.bot.client.send_followup_message(
                interaction_token=message["token"],
                embeds=[
                    {
                        "description": (
                            "あら?インスタンスが「実行中」ではないみたいですわ...\n"
                            "インスタンスの状態を確認してくださる?"
                        ),
                        "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                    }
                ],
            )
            return False
        else:
            return True

    @abstractmethod
    def __call__(self, message):
        raise NotImplementedError
