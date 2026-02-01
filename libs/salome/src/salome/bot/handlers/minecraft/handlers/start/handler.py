import os
from typing import TYPE_CHECKING

from salome.bot.handlers.minecraft.handlers.common import MinecraftActionHandler
from salome.config import Config
from salome.utils.aws import SSMClient

if TYPE_CHECKING:
    from salome.bot import SalomeBot


class MinecraftStartActionHandler(MinecraftActionHandler):
    def __init__(self, bot: SalomeBot):
        super().__init__(bot)

        self.world_name = os.environ["MINECRAFT_SERVER_WORLD_NAME"]

        self.ssm = SSMClient(region_name=self.instance_region)

    def __call__(self, message):
        if not self.is_server_stopped(message):
            return

        self.ec2.start_instance(self.instance_id)

        instance = self.ec2.describe_instance(self.instance_id)
        public_ip = instance["PublicIpAddress"]  # type: ignore

        command_id = self.ssm.send_command(
            instance_id=self.instance_id,
            commands=[
                "export HOME=/root",
                "source ~/.bashrc",
                f"cd /opt/minecraft/servers/{self.world_name}",
                "nohup bash run.sh > nohup.log 2>&1 &",
            ],
        )

        response = self.ssm.wait_for_command(command_id, self.instance_id)

        if response["Status"] != "Success":
            self.bot.client.send_followup_message(
                interaction_token=message["token"],
                embeds=[
                    {
                        "description": (
                            "あら?コマンドの実行に失敗したみたいですわ...\n"
                            "コマンドの履歴を確認してくださる?"
                        ),
                        "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                    }
                ],
            )
            return

        self.bot.client.send_followup_message(
            interaction_token=message["token"],
            embeds=[
                {
                    "description": (
                        f"Minecraftサーバ({self.world_name})を起動しましたわ！\n"
                        f"今回のIPアドレスは「{public_ip}」ですわね\n"
                        f"最後にサーバを停止するのをお忘れないようにしてくださいまし！"
                    ),
                    "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                }
            ],
        )
