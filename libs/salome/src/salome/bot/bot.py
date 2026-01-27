from salome.bot.handlers.ask import AskCommandHandler
from salome.bot.handlers.recipe import RecipeCommandHandler
from salome.utils.discord import DiscordClient


class SalomeBot:
    def __init__(self, client: DiscordClient):
        self.client = client

        self.ask = AskCommandHandler(self)
        self.recipe = RecipeCommandHandler(self)
