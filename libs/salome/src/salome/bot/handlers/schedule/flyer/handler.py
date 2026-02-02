import os
from typing import TYPE_CHECKING

import requests
from salome.bot.handlers.schedule.common import ScheduleHandler
from salome.config import Config

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
        ).json()

        shop = response["shop"]
        flyers = shop["chirashis"]["chirashi"]

        embeds = []
        for flyer in flyers:
            date = flyer["insertTime"].split()[0]
            pdf_url = f"https://ipqcache2.shufoo.net/c/{date}/c/{flyer['id']}/index/img/chirashi.pdf"

            embeds.append(
                {
                    "title": f"🛒 {flyer['title']}",
                    "url": pdf_url,
                    "description": (
                        f"**{shop['shopName']}**のチラシが届きましたわ！\n"
                        f"お買い得情報をぜひご覧くださいまし！\n\n"
                        f"📅 **掲載期間**\n"
                        f"{flyer['publishStartTime']} ～ {flyer['publishEndTime']}"
                    ),
                    "thumbnail": {"url": flyer["iconUrl"]},
                    "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                }
            )

        if embeds:
            self.bot.client.send_channel_message(
                channel_id=self.channel_id,
                embeds=embeds,
            )
