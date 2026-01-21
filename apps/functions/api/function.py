import json
import os

from discord_interactions import (
    InteractionResponseType,
    InteractionType,
    verify_key,
)
from fastapi import FastAPI, HTTPException, Request
from mangum import Mangum
from salome.utils.aws.sns import SNSClient

DISCORD_PUBLIC_KEY = os.environ["DISCORD_PUBLIC_KEY"]
SERVER_INTERACT_TOPIC_ARN = os.environ["SERVER_INTERACT_TOPIC_ARN"]

app = FastAPI()
sns_client = SNSClient()


@app.post("/webhook")
async def post_webhook(request: Request):
    rawbody = await request.body()
    headers = request.headers

    if not verify_key(
        rawbody,
        headers["x-signature-ed25519"],
        headers["x-signature-timestamp"],
        DISCORD_PUBLIC_KEY,
    ):
        raise HTTPException(status_code=401)

    body = json.loads(rawbody)
    interaction_type: int = body["type"]

    match interaction_type:
        case InteractionType.PING:
            return {
                "type": InteractionResponseType.PONG,
            }
        case InteractionType.APPLICATION_COMMAND:
            if command := body["data"].get("name"):
                sns_client.publish(
                    topic_arn=SERVER_INTERACT_TOPIC_ARN,
                    message=rawbody.decode(),
                    message_attributes={
                        "command": {
                            "DataType": "String",
                            "StringValue": command,
                        }
                    },
                )

            return {
                "type": InteractionResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE,
            }
        case _:
            raise HTTPException(status_code=400)


handler = Mangum(app)
