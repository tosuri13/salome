import os
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
        flyers: list[dict] = shop["chirashis"]["chirashi"]

        if not flyers:
            self.bot.client.send_channel_message(
                channel_id=self.channel_id,
                embeds=[
                    {
                        "title": "🥺 今週のチラシはまだ届いてないようですわ...",
                        "description": (
                            "今週分のチラシが見つかりませんでしたわ...日を空けて**公式サイト**を確認することをお勧めしますわ！\n"
                            f"・https://www.shufoo.net/pntweb/shopDetail/{self.flyer_shuhoo_shop_id}"
                        ),
                        "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                    }
                ],
            )
            return

        agent = SalomeFlyerAgent()

        contents = []
        flyer_embeds = []

        for flyer in flyers:
            date = flyer["insertTime"].split()[0]

            pdf_url = f"https://ipqcache2.shufoo.net/c/{date}/c/{flyer['id']}/index/img/chirashi.pdf"
            thumbnail_url = f"https://ipqcache2.shufoo.net/c/{date}/c/{flyer['id']}/index/img/thumb/thumb_l.jpg"

            contents.append(requests.get(pdf_url).content)
            flyer_embeds.append(
                {
                    "title": f"🛒 {flyer['title']}",
                    "url": pdf_url,
                    "fields": [
                        {
                            "name": "📅 掲載期間",
                            "value": f"{flyer['publishStartTime']} ～ {flyer['publishEndTime']}",
                            "inline": False,
                        }
                    ],
                    "thumbnail": {"url": thumbnail_url},
                    "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                }
            )

        result = agent.run(contents)
        cost = calc_inference_cost(result.usage, agent.ippt, agent.ottp)

        self.bot.client.send_channel_message(
            channel_id=self.channel_id,
            embeds=[
                *flyer_embeds,
                {
                    "title": "📑 今週のチラシまとめですわ！",
                    "description": (
                        f"{result.summary}\n"
                        "\n"
                        f"> この通知で{cost}ドルいただきましたわ〜！"
                    ),
                    "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                },
            ],
        )
