import os

from rich.console import Console
from salome.utils.discord import DiscordClient


class OptionType:
    STRING = 3


DISCORD_APPLICATION_ID = os.environ["DISCORD_APPLICATION_ID"]
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

console = Console()
discord_client = DiscordClient(DISCORD_APPLICATION_ID, DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    console.print("✨ Slash Commandsを登録します", style="cyan")

    for cmd in discord_client.get_commands():
        discord_client.delete_command(cmd["id"])

    commands = [
        {
            "name": "ask",
            "description": "何でも聞きたいことを質問してみよう!!",
            "options": [
                {
                    "name": "question",
                    "description": "質問",
                    "required": True,
                    "type": OptionType.STRING,
                }
            ],
        },
    ]

    for cmd in commands:
        discord_client.create_command(cmd)
        console.print(f"  ⏺ REGIST: {cmd['name']}", style="green")

    console.print("✅ Slash Commandsの登録が完了しました!", style="bold green")
