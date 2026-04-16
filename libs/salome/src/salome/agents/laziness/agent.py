from dataclasses import dataclass
from pathlib import Path
from string import Template

from salome.agents.prompts import SALOME_ROLE_PROMPT
from salome.config import Config
from strands import Agent
from strands.models import BedrockModel
from strands.types.event_loop import Usage

PROMPTS_PATH = Path(__file__).parent / "prompts"


@dataclass
class SalomeLazinessAgentResult:
    comment: str
    usage: Usage


class SalomeLazinessAgent:
    def __init__(self):
        self.system = SALOME_ROLE_PROMPT
        self.user_template = Template((PROMPTS_PATH / "user.md").read_text())

        self.model_id = Config.DEFAULT_GENERATIVE_MODEL_ID
        self.ippt = Config.DEFAULT_GENERATIVE_MODEL_IPPT
        self.oppt = Config.DEFAULT_GENERATIVE_MODEL_OPPT

    def run(self, summary: str, chart_image: bytes) -> SalomeLazinessAgentResult:
        user = self.user_template.substitute(summary=summary)

        agent = Agent(
            model=BedrockModel(
                region_name=Config.DEFAULT_REGION_NAME,
                model_id=self.model_id,
                temperature=0.0,
                max_tokens=256,
            ),
            system_prompt=self.system,
        )
        result = agent(
            [
                {"text": user},
                {
                    "image": {
                        "format": "png",
                        "source": {"bytes": chart_image},
                    },
                },
            ]
        )

        comment = str(result).strip()
        usage = result.metrics.accumulated_usage

        return SalomeLazinessAgentResult(comment, usage)
