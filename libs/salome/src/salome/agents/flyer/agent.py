from dataclasses import dataclass
from pathlib import Path

from salome.agents.prompts import SALOME_ROLE_PROMPT
from salome.config import Config
from strands import Agent
from strands.handlers import PrintingCallbackHandler
from strands.models import BedrockModel
from strands.types.event_loop import Usage

PROMPTS_PATH = Path(__file__).parent / "prompts"


@dataclass
class SalomeFlyerAgentResult:
    summary: str
    usage: Usage


class SalomeFlyerAgent:
    def __init__(self):
        self.system = SALOME_ROLE_PROMPT
        self.user = (PROMPTS_PATH / "user.md").read_text()

        # NOTE: Haiku 4.5では有用な画像認識ができないため、このエージェントではSonnet 4.5を使用して解析を行う
        self.model_id = "jp.anthropic.claude-sonnet-4-5-20250929-v1:0"
        self.ippt = 0.003
        self.ottp = 0.015

    def run(self, flyer: bytes, debug: bool = False) -> SalomeFlyerAgentResult:
        agent = Agent(
            model=BedrockModel(
                region_name=Config.DEFAULT_REGION_NAME,
                model_id=self.model_id,
                temperature=0.0,
                max_tokens=8192,
            ),
            callback_handler=PrintingCallbackHandler() if debug else None,
            system_prompt=self.system,
        )
        result = agent(
            [
                {"text": self.user},
                {
                    "document": {
                        "format": "pdf",
                        "name": "Supermarket Flyer",
                        "source": {
                            "bytes": flyer,
                        },
                    },
                },
            ]
        )

        summary = str(result).strip()
        usage = result.metrics.accumulated_usage

        return SalomeFlyerAgentResult(summary, usage)
