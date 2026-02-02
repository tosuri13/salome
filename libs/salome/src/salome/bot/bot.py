from salome.bot.handlers import (
    AskCommandHandler,
    FlyerScheduleHandler,
    GarbageScheduleHandler,
    MinecraftCommandHandler,
    RecipeCommandHandler,
)
from salome.utils.discord import DiscordClient


class SalomeBot:
    def __init__(self, client: DiscordClient):
        self.client = client

    @property
    def ask(self) -> AskCommandHandler:
        return AskCommandHandler(self)

    @property
    def minecraft(self) -> MinecraftCommandHandler:
        return MinecraftCommandHandler(self)

    @property
    def recipe(self) -> RecipeCommandHandler:
        return RecipeCommandHandler(self)

    @property
    def flyer(self) -> FlyerScheduleHandler:
        return FlyerScheduleHandler(self)

    @property
    def garbage(self) -> GarbageScheduleHandler:
        return GarbageScheduleHandler(self)
