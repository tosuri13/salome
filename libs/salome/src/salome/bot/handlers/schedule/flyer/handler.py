import os
import re
from typing import TYPE_CHECKING

import requests
from salome.agents import SalomeFlyerAgent
from salome.bot.handlers.schedule.common import ScheduleHandler
from salome.config import Config
from salome.utils import calc_inference_cost

if TYPE_CHECKING:
    from salome.bot import SalomeBot


class FlyerScheduleHandler(ScheduleHandler):
    def __init__(self, bot: "SalomeBot"):
        super().__init__(bot)

        self.channel_id = os.environ["DISCORD_CHANNEL_ID"]

        self.flyer_shuhoo_user_name = os.environ["FLYER_SHUFOO_USER_NAME"]
        self.flyer_shuhoo_shop_id = os.environ["FLYER_SHUFOO_SHOP_ID"]
        self.flyer_shuhoo_referer = os.environ["FLYER_SHUFOO_REFERER"]

    def __call__(self):
        response = requests.get(
            "https://asp.shufoo.net/api/shopDetailXML.php",
            params={
                "un": self.flyer_shuhoo_user_name,
                "shopId": self.flyer_shuhoo_shop_id,
                "responseFormat": "json",
            },
            headers={
                "Referer": self.flyer_shuhoo_referer,
            },
        )
        response = response.json()

        shop = response["shop"]
        flyers = shop["chirashis"]["chirashi"]

        agent = SalomeFlyerAgent()

        for flyer in flyers:
            if not re.search(r"\d{1,2}/\d{1,2}[～〜]\d{1,2}/\d{1,2}", flyer["title"]):
                continue

            date = flyer["insertTime"].split()[0]
            pdf_url = f"https://ipqcache2.shufoo.net/c/{date}/c/{flyer['id']}/index/img/chirashi.pdf"

            result = agent.run(requests.get(pdf_url).content)
            cost = calc_inference_cost(result.usage, agent.ippt, agent.ottp)

            self.bot.client.send_channel_message(
                channel_id=self.channel_id,
                embeds=[
                    {
                        "title": "今週のチラシが届きましたわ〜！",
                        "url": pdf_url,
                        "description": (
                            f"{result.summary}\n"
                            "\n"
                            f"📅 **掲載期間**\n"
                            f"{flyer['publishStartTime']} ～ {flyer['publishEndTime']}\n"
                            "\n"
                            f"> この通知で{cost}ドルいただきましたわ〜！"
                        ),
                        "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                    }
                ],
            )
