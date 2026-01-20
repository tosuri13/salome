import requests

DISCORD_API_BASEURL = "https://discord.com/api/v10"


class DiscordClient:
    def __init__(self, application_id: str, bot_token: str):
        self.application_id = application_id
        self.bot_token = bot_token

    def send_followup_message(
        self,
        interaction_token: str,
        content: str,
    ):
        response = requests.post(
            f"{DISCORD_API_BASEURL}/webhooks/{self.application_id}/{interaction_token}",
            json={"content": content},
            headers={
                "Authorization": f"Bot {self.bot_token}",
                "Content-Type": "application/json",
            },
        )

        if response.status_code != 200:
            raise ValueError(f"Discord API failed: {response.text}")
