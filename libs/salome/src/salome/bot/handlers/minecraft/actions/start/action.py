import os

from salome.utils.aws import EC2Client, SSMClient

from ..common import MinecraftActionHandler


class MinecraftStartActionHandler(MinecraftActionHandler):
    def __call__(self, message):
        if not self.require_stopped(message):
            return

        instance_id = os.environ["MINECRAFT_INSTANCE_ID"]
        server_version = os.environ["MINECRAFT_SERVER_VERSION"]
        instance_region = os.environ.get("MINECRAFT_INSTANCE_REGION", "ap-south-1")

        ec2 = EC2Client(region_name=instance_region)
        ssm = SSMClient(region_name=instance_region)

        ec2.start_instance(instance_id)

        instance = ec2.describe_instance(instance_id)
        public_ip = instance["PublicIpAddress"]

        command_id = ssm.send_command(
            instance_id=instance_id,
            commands=[
                "export HOME=/root",
                "source ~/.bashrc",
                f"cd /opt/minecraft/servers/{server_version}",
                "nohup bash run.sh > nohup.log 2>&1 &",
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
                f"Minecraftサーバ({server_version})を起動しましたわ！\n"
                f"今回のIPアドレスは「{public_ip}」ですわね\n"
                f"最後にサーバを停止するのをお忘れないようにしてくださいまし！"
            ),
        )
