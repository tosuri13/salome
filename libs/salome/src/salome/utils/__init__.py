from typing import TYPE_CHECKING

from salome.config import Config

if TYPE_CHECKING:
    from strands.types.event_loop import Usage


def calc_inference_cost(
    usage: "Usage",
    ippt: float = Config.DEFAULT_GENERATIVE_MODEL_IPPT,
    oppt: float = Config.DEFAULT_GENERATIVE_MODEL_OPPT,
) -> float:
    i_tokens = usage["inputTokens"]
    o_tokens = usage["outputTokens"]

    i_cost = i_tokens * ippt / 1000
    o_cost = o_tokens * oppt / 1000

    return round(i_cost + o_cost, ndigits=6)
