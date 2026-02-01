from salome.bot.handlers import (
    AskCommandHandler,
    MinecraftCommandHandler,
    RecipeCommandHandler,
)
from salome.utils.discord import DiscordClient


class SalomeBot:
    def __init__(self, client: DiscordClient):
        self.client = client

        self.ask = AskCommandHandler(self)
        self.minecraft = MinecraftCommandHandler(self)
        self.recipe = RecipeCommandHandler(self)
