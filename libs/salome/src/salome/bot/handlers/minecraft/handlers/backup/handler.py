import os
from datetime import datetime

from salome.utils.aws import SSMClient

from ..common import MinecraftActionHandler


class MinecraftBackupActionHandler(MinecraftActionHandler):
    def __call__(self, message):
        if not self.require_running(message):
            return

        instance_id = os.environ["MINECRAFT_INSTANCE_ID"]
        server_version = os.environ["MINECRAFT_SERVER_VERSION"]
        backup_bucket_name = os.environ["MINECRAFT_BACKUP_BUCKET_NAME"]
        instance_region = os.environ.get("MINECRAFT_INSTANCE_REGION", "ap-south-1")

        ssm = SSMClient(region_name=instance_region)

        upload_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        command_id = ssm.send_command(
            instance_id=instance_id,
            commands=[
                "export HOME=/root",
                "source ~/.bashrc",
                f"cd /opt/minecraft/servers/{server_version}",
                f"aws s3 cp world s3://{backup_bucket_name}/{server_version}/{upload_time}/world --recursive",
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

        self.bot.client.send_followup_message(
            interaction_token=message["token"],
            content=(
                "ワールドのバックアップを取得しましたわ!!\n"
                "ワールドの復旧は、わたくしではなくセバスチャン(開発者)に命令してくださいまし!!"
            ),
        )
