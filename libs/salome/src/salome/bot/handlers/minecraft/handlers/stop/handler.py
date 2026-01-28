import os
from datetime import datetime

from salome.utils.aws import EC2Client, SSMClient

from ..common import MinecraftActionHandler


class MinecraftStopActionHandler(MinecraftActionHandler):
    def __call__(self, message):
        if not self.require_running(message):
            return

        instance_id = os.environ["MINECRAFT_INSTANCE_ID"]
        server_version = os.environ["MINECRAFT_SERVER_VERSION"]
        backup_bucket_name = os.environ["MINECRAFT_BACKUP_BUCKET_NAME"]
        instance_region = os.environ.get("MINECRAFT_INSTANCE_REGION", "ap-south-1")

        ec2 = EC2Client(region_name=instance_region)
        ssm = SSMClient(region_name=instance_region)

        upload_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        command_id = ssm.send_command(
            instance_id=instance_id,
            commands=[
                "export HOME=/root",
                "source ~/.bashrc",
                f"cd /opt/minecraft/servers/{server_version}",
                f"aws s3 cp world s3://{backup_bucket_name}/{server_version}/{upload_time}/world --recursive",
                "mcrcon -w 5 stop",
            ],
        )

        response = ssm.wait_for_command(command_id, instance_id)

        if response["Status"] != "Success":
            self.bot.client.send_followup_message(
                interaction_token=message["token"],
                content=(
                    "あら?コマンドの実行に失敗したみたいですわ...\n"
                    "コマンドの履歴を確認してくださる?"
                ),
            )
            return

        ec2.stop_instance(instance_id)

        self.bot.client.send_followup_message(
            interaction_token=message["token"],
            content=(
                f"Minecraftサーバ({server_version})を停止しましたわ!!\n"
                f"自動でバックアップも保存しておりますわよ!!\n"
                f"また遊びたくなったら、いつでもわたくしをお呼びくださいまし!!"
            ),
        )
