from typing import TYPE_CHECKING

from salome.bot.handlers.minecraft.handlers.common import MinecraftActionHandler
from salome.config import Config

if TYPE_CHECKING:
    from salome.bot import SalomeBot


class MinecraftStatusActionHandler(MinecraftActionHandler):
    def __init__(self, bot: "SalomeBot"):
        super().__init__(bot)

    def __call__(self, message):
        instance = self.ec2.describe_instance(self.instance_id)

        match instance["State"]["Name"]:  # type: ignore
            case "running":
                description = (
                    "Minecraftサーバは「実行中」ですわ!!\n"
                    "誰も遊んでおられないのなら、わたくしにサーバの停止を命じてくださいまし!!"
                )
            case "stopped":
                description = (
                    "Minecraftサーバは「停止済み」ですわ!!\n"
                    "ふふっ、遊びたいのかしら?でしたら、わたくしにサーバの起動を命じてくださいまし!!"
                )
            case _:
                description = (
                    "あら?Minecraftサーバは「実行中」でも「停止済み」でもないみたいですわ...\n"
                    "少し時間をおいて、もう一度わたくしにサーバの確認を命じてもらえるかしら?"
                )

        self.bot.client.send_followup_message(
            interaction_token=message["token"],
            embeds=[
                {
                    "description": description,
                    "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                }
            ],
        )
