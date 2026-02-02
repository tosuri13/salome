import os
from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from salome.bot.handlers.schedule.common import ScheduleHandler
from salome.config import Config

if TYPE_CHECKING:
    from salome.bot import SalomeBot


class GarbageScheduleHandler(ScheduleHandler):
    def __init__(self, bot: "SalomeBot"):
        super().__init__(bot)

        self.channel_id = os.environ.get("DISCORD_CHANNEL_ID")

    def __call__(self) -> None:
        if self.channel_id is None:
            raise ValueError(
                "Missing required environment variable: DISCORD_CHANNEL_ID"
            )

        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        weekday = now.weekday()

        match weekday:
            case 0:
                embed = {
                    "title": "🛍️ プラ容器包装の日",
                    "description": (
                        "今日は「**容器包装プラスチック**」の日ですわ！\n"
                        "**朝8時まで**にお出しくださいまし！"
                    ),
                    "fields": [
                        {
                            "name": "対象のもの",
                            "value": (
                                "・お菓子の袋 / レジ袋\n"
                                "・カップ・パック類\n"
                                "・ペットボトルのキャップ・ラベル"
                            ),
                            "inline": False,
                        },
                    ],
                    "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                }
            case 1 | 4:
                embed = {
                    "title": "🔥 燃えるごみの日",
                    "description": (
                        "今日は「**燃えるごみ**」の日ですわ！\n"
                        "**朝8時まで**にお出しくださいまし！"
                    ),
                    "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                }
            case 5:
                embed = {
                    "title": "📦 ダンボール集荷の日",
                    "description": (
                        "今日は「**ダンボール集荷**」の日ですわ！\n"
                        "毎週とは限りませんので、**お昼頃まで**に周りの雰囲気を見てお出ししてほしいですわ〜"
                    ),
                    "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                }
            case 2:
                embed = {
                    "title": "🥫 缶・びん・ペットボトルの日",
                    "description": (
                        "今日は「**缶・びん・ペットボトル**」の日ですわ！\n"
                        "**朝8時まで**にお出しくださいまし！"
                    ),
                    "fields": [
                        {
                            "name": "対象のもの",
                            "value": (
                                "・アルミ缶 / スチール缶\n"
                                "・ガラスびん\n"
                                "・ペットボトル（キャップとラベルはプラ容器包装へ）"
                            ),
                            "inline": False,
                        },
                    ],
                    "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                }
            case 3 if (now.day - 1) // 7 + 1 in (2, 4):
                embed = {
                    "title": "🧲 燃えないごみの日",
                    "description": (
                        "今日は「**燃えないごみ**」と「**カセットボンベ・スプレー缶**」の日ですわ！\n"
                        "**朝8時まで**にお出しくださいまし！"
                    ),
                    "fields": [
                        {
                            "name": "🔩 燃えないごみ",
                            "value": (
                                "・金属類 / 陶磁器類\n・ガラス製品 / 小型家電 など"
                            ),
                            "inline": False,
                        },
                        {
                            "name": "🧴 カセットボンベ・スプレー缶",
                            "value": (
                                "・カセットボンベ\n"
                                "・スプレー缶（整髪料・殺虫剤など）\n\n"
                                "> ⚠️ **中身は全部使い切って**くださいまし！\n"
                                "> ⚠️ **穴あけは不要**ですわ！\n"
                                "> ⚠️ 燃えないごみと**分けて**、"
                                "**中身の見える袋**（15L以下）で出してくださいまし！\n"
                                "> ⚠️ クリーンステーションでも燃えないごみと"
                                "**場所を分けて**置いてくださいまし！"
                            ),
                            "inline": False,
                        },
                    ],
                    "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                }
            case _:
                return

        self.bot.client.send_channel_message(
            channel_id=self.channel_id,
            embeds=[embed],
        )
