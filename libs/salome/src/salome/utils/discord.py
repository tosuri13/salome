from typing import Any

import requests

DISCORD_API_BASEURL = "https://discord.com/api/v10"


class DiscordClient:
    def __init__(self, application_id: str, bot_token: str):
        self.application_id = application_id
        self.bot_token = bot_token

        self._headers = {
            "Authorization": f"Bot {self.bot_token}",
            "Content-Type": "application/json",
        }

    def send_followup_message(self, interaction_token: str, content: str):
        response = requests.post(
            f"{DISCORD_API_BASEURL}/webhooks/{self.application_id}/{interaction_token}",
            headers=self._headers,
            json={
                "content": content,
            },
        )

        if response.status_code != 200:
            raise ValueError(f"Discord API failed: {response.text}")

    def get_commands(self) -> list[dict[str, Any]]:
        response = requests.get(
            f"{DISCORD_API_BASEURL}/applications/{self.application_id}/commands",
            headers=self._headers,
        )

        if response.status_code != 200:
            raise ValueError(f"Discord API failed: {response.text}")

        return response.json()

    def create_command(self, commands: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(
            f"{DISCORD_API_BASEURL}/applications/{self.application_id}/commands",
            headers=self._headers,
            json=commands,
        )

        if response.status_code not in (200, 201):
            raise ValueError(f"Discord API failed: {response.text}")

        return response.json()

    def delete_command(self, command_id: str):
        response = requests.delete(
            f"{DISCORD_API_BASEURL}/applications/{self.application_id}/commands/{command_id}",
            headers=self._headers,
        )

        if response.status_code != 204:
            raise ValueError(f"Discord API failed: {response.text}")
