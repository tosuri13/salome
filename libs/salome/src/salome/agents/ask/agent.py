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
    def __init__(self):
        self.system = SALOME_ROLE_PROMPT

    def run(self, question: str, debug: bool = False) -> SalomeAskAgentResult:
        agent = Agent(
            model=BedrockModel(
                region_name=Config.DEFAULT_REGION_NAME,
                model_id=Config.DEFAULT_GENERATIVE_MODEL_ID,
                temperature=0.0,
                max_tokens=8192,
            ),
            callback_handler=PrintingCallbackHandler() if debug else None,
            system_prompt=self.system,
        )
        result = agent(question)

        answer = str(result).strip()
        usage = result.metrics.accumulated_usage

        return SalomeAskAgentResult(answer, usage)
