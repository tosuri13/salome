import json
import os

from salome.utils.discord import DiscordClient

DISCORD_APPLICATION_ID = os.environ["DISCORD_APPLICATION_ID"]
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

discord_client = DiscordClient(
    DISCORD_APPLICATION_ID,
    DISCORD_BOT_TOKEN,
)


def handler(event, context):
    record = event["Records"][0]
    message = json.loads(record["Sns"]["Message"])

    discord_client.send_followup_message(
        interaction_token=message["token"],
        content="Hello from Salome!",
    )
