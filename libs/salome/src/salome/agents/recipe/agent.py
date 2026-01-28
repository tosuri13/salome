from dataclasses import dataclass
from pathlib import Path
from string import Template

from salome.agents.prompts import SALOME_ROLE_PROMPT
from salome.agents.recipe.tools import RecipeTools
from salome.config import Config
from strands import Agent
from strands.handlers import PrintingCallbackHandler
from strands.models import BedrockModel
from strands.types.event_loop import Usage

PROMPTS_PATH = Path(__file__).parent / "prompts"


@dataclass
class SalomeRecipeAgentResult:
    answer: str
    usage: Usage


class SalomeRecipeAgent:
    def __init__(self):
        self.system = SALOME_ROLE_PROMPT
        self.user_template = Template((PROMPTS_PATH / "user.md").read_text())

        self.recipe_tools = RecipeTools()

    def run(self, order: str, debug: bool = False) -> SalomeRecipeAgentResult:
        user = self.user_template.substitute(order=order)

        agent = Agent(
            model=BedrockModel(
                region_name=Config.DEFAULT_REGION_NAME,
                model_id=Config.DEFAULT_GENERATIVE_MODEL_ID,
                temperature=0.0,
                max_tokens=8192,
            ),
            callback_handler=PrintingCallbackHandler() if debug else None,
            system_prompt=self.system,
            tools=self.recipe_tools(),
        )
        result = agent(user)

        answer = str(result).strip()
        usage = result.metrics.accumulated_usage

        return SalomeRecipeAgentResult(answer, usage)
