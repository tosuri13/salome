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
    raw_body = await request.body()
    headers = request.headers

    if not verify_key(
        raw_body,
        headers["x_signature_ed25519"],
        headers["x_signature_timestamp"],
        DISCORD_PUBLIC_KEY,
    ):
        raise HTTPException(status_code=401)

    body = json.loads(raw_body)
    interaction_type: int = body["type"]

    if interaction_type == InteractionType.PING:
        return {
            "type": InteractionResponseType.PONG,
        }

    if interaction_type == InteractionType.APPLICATION_COMMAND:
        if command := body["data"].get("name"):
            sns_client.publish(
                topic_arn=SERVER_INTERACT_TOPIC_ARN,
                message=raw_body.decode(),
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

    raise HTTPException(status_code=400, detail="Unknown interaction type")


handler = Mangum(app)
