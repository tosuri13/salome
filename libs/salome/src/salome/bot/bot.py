from salome.bot.handlers.ask import AskCommandHandler


class SalomeBotHandler:
    def __init__(self, bot: SalomeBot):
        self.bot = bot


class SalomeBot:
    def __init__(self):
        self.ask = AskCommandHandler(self)
