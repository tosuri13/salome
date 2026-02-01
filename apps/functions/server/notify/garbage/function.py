import os

from salome.bot import SalomeBot
from salome.utils.discord import DiscordClient

DISCORD_APPLICATION_ID = os.environ["DISCORD_APPLICATION_ID"]
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

client = DiscordClient(DISCORD_APPLICATION_ID, DISCORD_BOT_TOKEN)
bot = SalomeBot(client)


def handler(event, context):
    bot.garbage()
