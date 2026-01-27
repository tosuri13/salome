import os
from datetime import datetime
from enum import Enum
from typing import Any

from salome.bot.handlers import CommandHandler
from salome.utils.aws import EC2Client, SSMClient
from salome.utils.discord import CommandOptionType


class MinecraftAction(str, Enum):
    START = "start"
    STOP = "stop"
    STATUS = "status"
    BACKUP = "backup"


class MinecraftCommandHandler(CommandHandler):
    option = {
        "name": "minecraft",
        "description": "Minecraftサーバーを操作しよう!!",
        "options": [
            {
                "name": "action",
                "description": "実行するアクション",
                "required": True,
                "type": CommandOptionType.STRING,
                "choices": [
                    {"name": action, "value": action} for action in MinecraftAction
                ],
            }
        ],
    }

    def __init__(self, bot):
        super().__init__(bot)

        self.instance_id = os.environ["MINECRAFT_INSTANCE_ID"]
        self.server_version = os.environ["MINECRAFT_SERVER_VERSION"]
        self.backup_bucket_name = os.environ["MINECRAFT_BACKUP_BUCKET_NAME"]
        self.instance_region = os.environ.get("MINECRAFT_INSTANCE_REGION", "ap-south-1")

        self.ec2 = EC2Client(region_name=self.instance_region)
        self.ssm = SSMClient(region_name=self.instance_region)

    def __call__(self, message: dict[str, Any]):
        options = self.parse_options(message)
        self._interaction_token: str = message["token"]

        match action := options["action"]:
            case MinecraftAction.START:
                content = self._start()
            case MinecraftAction.STOP:
                content = self._stop()
            case MinecraftAction.STATUS:
                content = self._status()
            case MinecraftAction.BACKUP:
                content = self._backup()
            case _:
                raise ValueError(f"Unsupported action: {action}")

        self.bot.client.send_followup_message(
            interaction_token=self._interaction_token,
            content=content,
        )

    def _start(self) -> str:
        instance = self.ec2.describe_instance(self.instance_id)
        state_name = instance["State"]["Name"]  # type: ignore

        if state_name != "stopped":
            return (
                "あら?インスタンスが「停止済み」ではないみたいですわ...\n"
                "インスタンスの状態を確認してくださる?"
            )

        self.ec2.start_instance(self.instance_id)

        instance = self.ec2.describe_instance(self.instance_id)
        public_ip = instance["PublicIpAddress"]  # type: ignore

        command_id = self.ssm.send_command(
            instance_id=self.instance_id,
            commands=[
                "export HOME=/root",
                "source ~/.bashrc",
                f"cd /opt/minecraft/servers/{self.server_version}",
                "nohup bash run.sh > nohup.log 2>&1 &",
            ],
        )

        response = self.ssm.wait_for_command(command_id, self.instance_id)

        if response["Status"] != "Success":
            return (
                "あら?コマンドの実行に失敗したみたいですわ...\n"
                "コマンドの履歴を確認してくださる?"
            )

        return (
            f"Minecraftサーバ({self.server_version})を起動しましたわ！\n"
            f"今回のIPアドレスは「{public_ip}」ですわね\n"
            f"最後にサーバを停止するのをお忘れないようにしてくださいまし！"
        )

    def _stop(self) -> str:
        instance = self.ec2.describe_instance(self.instance_id)
        state_name = instance["State"]["Name"]  # type: ignore

        if state_name != "running":
            return (
                "あら?インスタンスが「実行中」ではないみたいですわ...\n"
                "インスタンスの状態を確認してくださる?"
            )

        upload_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        command_id = self.ssm.send_command(
            instance_id=self.instance_id,
            commands=[
                "export HOME=/root",
                "source ~/.bashrc",
                f"cd /opt/minecraft/servers/{self.server_version}",
                f"aws s3 cp world s3://{self.backup_bucket_name}/{self.server_version}/{upload_time}/world --recursive",
                "mcrcon -w 5 stop",
            ],
        )

        response = self.ssm.wait_for_command(command_id, self.instance_id)

        if response["Status"] != "Success":
            return (
                "あら?コマンドの実行に失敗したみたいですわ...\n"
                "コマンドの履歴を確認してくださる?"
            )

        self.ec2.stop_instance(self.instance_id)

        return (
            f"Minecraftサーバ({self.server_version})を停止しましたわ!!\n"
            f"自動でバックアップも保存しておりますわよ!!\n"
            f"また遊びたくなったら、いつでもわたくしをお呼びくださいまし!!"
        )

    def _status(self) -> str:
        instance = self.ec2.describe_instance(self.instance_id)
        state_name = instance["State"]["Name"]  # type: ignore

        match state_name:
            case "running":
                return (
                    "Minecraftサーバは「実行中」ですわ!!\n"
                    "誰も遊んでおられないのなら、わたくしにサーバの停止を命じてくださいまし!!"
                )
            case "stopped":
                return (
                    "Minecraftサーバは「停止済み」ですわ!!\n"
                    "ふふっ、遊びたいのかしら?でしたら、わたくしにサーバの起動を命じてくださいまし!!"
                )
            case _:
                return (
                    "あら?Minecraftサーバは「実行中」でも「停止済み」でもないみたいですわ...\n"
                    "少し時間をおいて、もう一度わたくしにサーバの確認を命じてもらえるかしら?"
                )

    def _backup(self) -> str:
        instance = self.ec2.describe_instance(self.instance_id)
        state_name = instance["State"]["Name"]  # type: ignore

        if state_name != "running":
            return (
                "あら?インスタンスが「実行中」ではないみたいですわ...\n"
                "インスタンスの状態を確認してくださる?"
            )

        upload_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        command_id = self.ssm.send_command(
            instance_id=self.instance_id,
            commands=[
                "export HOME=/root",
                "source ~/.bashrc",
                f"cd /opt/minecraft/servers/{self.server_version}",
                f"aws s3 cp world s3://{self.backup_bucket_name}/{self.server_version}/{upload_time}/world --recursive",
            ],
        )

        response = self.ssm.wait_for_command(command_id, self.instance_id)

        if response["Status"] != "Success":
            return (
                "あら?コマンドの実行に失敗したみたいですわ...\n"
                "コマンドの履歴を確認してくださる?"
            )

        return (
            "ワールドのバックアップを取得しましたわ!!\n"
            "ワールドの復旧は、わたくしではなくセバスチャン(開発者)に命令してくださいまし!!"
        )
