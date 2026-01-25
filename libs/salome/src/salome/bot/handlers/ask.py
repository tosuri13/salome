from typing import TypedDict

from salome.agents import SalomeAskAgent
from salome.bot import SalomeBotHandler


class AskCommandOptions(TypedDict):
    question: str


class AskCommandHandler(SalomeBotHandler):
    def __call__(self, options: AskCommandOptions) -> str:
        agent = SalomeAskAgent()
        result = agent.run(options["question"])

        return result.answer
