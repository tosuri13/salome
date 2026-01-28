import os

from salome.utils.aws import EC2Client

from ..common import MinecraftActionHandler


class MinecraftStatusActionHandler(MinecraftActionHandler):
    def __call__(self, message):
        instance_id = os.environ["MINECRAFT_INSTANCE_ID"]
        instance_region = os.environ.get("MINECRAFT_INSTANCE_REGION", "ap-south-1")

        ec2 = EC2Client(region_name=instance_region)

        instance = ec2.describe_instance(instance_id)
        state_name = instance["State"]["Name"]

        match state_name:
            case "running":
                content = (
                    "Minecraftサーバは「実行中」ですわ!!\n"
                    "誰も遊んでおられないのなら、わたくしにサーバの停止を命じてくださいまし!!"
                )
            case "stopped":
                content = (
                    "Minecraftサーバは「停止済み」ですわ!!\n"
                    "ふふっ、遊びたいのかしら?でしたら、わたくしにサーバの起動を命じてくださいまし!!"
                )
            case _:
                content = (
                    "あら?Minecraftサーバは「実行中」でも「停止済み」でもないみたいですわ...\n"
                    "少し時間をおいて、もう一度わたくしにサーバの確認を命じてもらえるかしら?"
                )

        self.bot.client.send_followup_message(
            interaction_token=message["token"],
            content=content,
        )
