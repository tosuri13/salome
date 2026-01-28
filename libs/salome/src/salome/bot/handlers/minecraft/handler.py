from enum import Enum
from typing import Any

from salome.bot.handlers.common import CommandHandler
from salome.utils.discord import CommandOptionType

from .actions import (
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


class MinecraftHandler(CommandHandler):
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
