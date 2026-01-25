from dataclasses import dataclass

from salome.agents.prompts import SALOME_ROLE_PROMPT
from salome.config import Config
from strands import Agent
from strands.handlers import PrintingCallbackHandler
from strands.models import BedrockModel
from strands.types.event_loop import Usage


@dataclass
class SalomeAskAgentResult:
    answer: str
    usage: Usage


class SalomeAskAgent:
    def __init__(
        self,
        model_id: str = Config.DEFAULT_MODEL_ID,
        region_name: str = Config.DEFAULT_REGION_NAME,
    ):
        self.model_id = model_id
        self.region_name = region_name

        self.system = SALOME_ROLE_PROMPT

    def run(self, question: str, debug: bool = False) -> SalomeAskAgentResult:
        agent = Agent(
            model=BedrockModel(
                region_name=self.region_name,
                model_id=self.model_id,
            ),
            callback_handler=PrintingCallbackHandler() if debug else None,
            system_prompt=self.system,
        )
        result = agent(question)

        return SalomeAskAgentResult(
            str(result).strip(),
            result.metrics.accumulated_usage,
        )
