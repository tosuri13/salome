import os
from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from salome.bot.handlers.minecraft.handlers.common import MinecraftActionHandler
from salome.config import Config
from salome.utils.aws import SSMClient

if TYPE_CHECKING:
    from salome.bot import SalomeBot


class MinecraftStopActionHandler(MinecraftActionHandler):
    def __init__(self, bot: "SalomeBot"):
        super().__init__(bot)

        self.world_name = os.environ["MINECRAFT_SERVER_WORLD_NAME"]
        self.backup_bucket_name = os.environ["MINECRAFT_BACKUP_BUCKET_NAME"]

        self.ssm = SSMClient(region_name=self.instance_region)

    def __call__(self, message):
        if not self.is_server_running(message):
            return

        upload_time = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d-%H%M%S")
        command_id = self.ssm.send_command(
            instance_id=self.instance_id,
            commands=[
                "export HOME=/root && source ~/.bashrc",
                f"cd /opt/minecraft/servers/{self.world_name}",
                f"aws s3 cp world s3://{self.backup_bucket_name}/{self.world_name}/{upload_time}/world --recursive",
                "mcrcon -w 5 stop",
            ],
        )

        response = self.ssm.wait_for_command(command_id, self.instance_id)

        if response["Status"] != "Success":
            self.bot.client.send_followup_message(
                interaction_token=message["token"],
                embeds=[
                    {
                        "description": (
                            "あら？コマンドの実行に失敗したみたいですわ...\n"
                            "コマンドの履歴を確認してくださるかしら？"
                        ),
                        "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                    }
                ],
            )
            return

        self.ec2.stop_instance(self.instance_id)

        self.bot.client.send_followup_message(
            interaction_token=message["token"],
            embeds=[
                {
                    "description": (
                        f"Minecraftサーバ(**{self.world_name}**)を停止しましたわ〜\n"
                        f"また遊びたくなったら、いつでもわたくしをお呼びくださいまし！"
                    ),
                    "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                }
            ],
        )
