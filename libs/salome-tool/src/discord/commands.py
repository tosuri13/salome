import os

from rich.console import Console
from salome.bot.handlers import (
    AskCommandHandler,
    MinecraftCommandHandler,
    RecipeCommandHandler,
)
from salome.bot.handlers.common import CommandHandler
from salome.utils.discord import DiscordClient

DISCORD_APPLICATION_ID = os.environ["DISCORD_APPLICATION_ID"]
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

console = Console()
client = DiscordClient(DISCORD_APPLICATION_ID, DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    console.print("✨ Slash Commandsを登録します", style="cyan")

    for cmd in client.get_commands():
        client.delete_command(cmd["id"])

    handlers: list[type[CommandHandler]] = [
        AskCommandHandler,
        MinecraftCommandHandler,
        RecipeCommandHandler,
    ]
    commands = [handler.option for handler in handlers]

    for cmd in commands:
        client.create_command(cmd)
        console.print(f"  ⏺ REGIST: {cmd['name']}", style="green")

    console.print("✅ Slash Commandsの登録が完了しました!", style="bold green")
