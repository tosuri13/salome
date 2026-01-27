from typing import Any

from salome.agents import SalomeRecipeAgent
from salome.bot.handlers import CommandHandler
from salome.utils import calc_inference_cost
from salome.utils.discord import CommandOptionType


class RecipeCommandHandler(CommandHandler):
    option = {
        "name": "recipe",
        "description": "お料理のレシピを教えてもらおう!!",
        "options": [
            {
                "name": "order",
                "description": "レシピの登録や検索などの指示",
                "required": True,
                "type": CommandOptionType.STRING,
            }
        ],
    }

    def __call__(self, message: dict[str, Any]) -> None:
        options = self.parse_options(message)
        interaction_token = message["token"]

        agent = SalomeRecipeAgent()
        result = agent.run(options["order"])

        self.bot.client.send_followup_message(
            interaction_token=interaction_token,
            content=(
                result.answer
                + "\n\n"
                + f"> この回答で{calc_inference_cost(result.usage)}ドルいただきましたわ〜！"
            ),
        )
