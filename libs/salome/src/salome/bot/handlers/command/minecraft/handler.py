from enum import Enum
from typing import Any

from salome.bot.handlers.command.common import CommandHandler
from salome.utils.discord import CommandOptionType

from .handlers import (
    MinecraftBackupActionHandler,
    MinecraftStartActionHandler,
    MinecraftStatusActionHandler,
    MinecraftStopActionHandler,
)


class MinecraftAction(str, Enum):
    START = "start"
    STOP = "stop"
    STATUS = "status"
    BACKUP = "backup"

    @property
    def label(self) -> str:
        return {
            MinecraftAction.START: "サーバを起動する",
            MinecraftAction.STOP: "サーバを停止する",
            MinecraftAction.STATUS: "サーバの状態を確認する",
            MinecraftAction.BACKUP: "バックアップを取得する",
        }[self]


class MinecraftCommandHandler(CommandHandler):
    option = {
        "name": "minecraft",
        "description": "Minecraftサーバーを操作しよう！",
        "options": [
            {
                "name": "action",
                "description": "実行するアクション",
                "required": True,
                "type": CommandOptionType.STRING,
                "choices": [
                    {
                        "name": action.label,
                        "value": action.value,
                    }
                    for action in MinecraftAction
                ],
            }
        ],
    }

    def __call__(self, message: dict[str, Any]):
        options = self.parse_options(message)

        match options["action"]:
            case MinecraftAction.START:
                handler = MinecraftStartActionHandler(self.bot)
            case MinecraftAction.STOP:
                handler = MinecraftStopActionHandler(self.bot)
            case MinecraftAction.STATUS:
                handler = MinecraftStatusActionHandler(self.bot)
            case MinecraftAction.BACKUP:
                handler = MinecraftBackupActionHandler(self.bot)

        handler(message)
