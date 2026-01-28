from typing import Any

from salome.agents import SalomeAskAgent
from salome.bot.handlers import CommandHandler
from salome.utils import calc_inference_cost
from salome.utils.discord import CommandOptionType


class AskCommandHandler(CommandHandler):
    option = {
        "name": "ask",
        "description": "何でも聞きたいことを質問してみよう!!",
        "options": [
            {
                "name": "question",
                "description": "質問",
                "required": True,
                "type": CommandOptionType.STRING,
            }
        ],
    }

    def __call__(self, message: dict[str, Any]) -> None:
        options = self.parse_options(message)
        interaction_token = message["token"]

        agent = SalomeAskAgent()
        result = agent.run(options["question"])

        self.bot.client.send_followup_message(
            interaction_token=interaction_token,
            content=(
                result.answer
                + "\n\n"
                + f"> この回答で{calc_inference_cost(result.usage)}ドルいただきましたわ〜！"
            ),
        )
