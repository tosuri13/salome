from salome.config import Config
from strands.types.event_loop import Usage


def calc_inference_cost(usage: Usage) -> float:
    i_tokens = usage["inputTokens"]
    o_tokens = usage["outputTokens"]

    i_cost = i_tokens * Config.DEFAULT_GENERATIVE_MODEL_IPPT / 1000
    o_cost = o_tokens * Config.DEFAULT_GENERATIVE_MODEL_OPPT / 1000

    return round(i_cost + o_cost, ndigits=6)
