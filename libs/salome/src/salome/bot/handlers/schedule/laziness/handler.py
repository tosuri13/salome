import io
import os
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from salome.agents import SalomeLazinessAgent
from salome.bot.handlers.schedule.common import ScheduleHandler
from salome.config import Config
from salome.utils.aws import DynamoDBClient

if TYPE_CHECKING:
    from salome.bot import SalomeBot


class LazinessScheduleHandler(ScheduleHandler):
    def __init__(self, bot: "SalomeBot"):
        super().__init__(bot)

        self.channel_id = os.environ["DISCORD_CHANNEL_ID"]
        self.table_name = os.environ["LAZYCAM_RECORDS_TABLE_NAME"]

        self.dynamodb = DynamoDBClient()

    def __call__(self) -> None:
        yesterday = datetime.now(ZoneInfo("Asia/Tokyo")) - timedelta(days=1)

        response = self.dynamodb.query(
            TableName=self.table_name,
            KeyConditionExpression="#d = :date",
            ExpressionAttributeNames={"#d": "date"},
            ExpressionAttributeValues={
                ":date": {
                    "S": yesterday.strftime("%Y-%m-%d"),
                }
            },
        )
        records = response["Items"]

        if not records:
            self.bot.client.send_channel_message(
                channel_id=self.channel_id,
                embeds=[
                    {
                        "title": "🛏️ 昨日のゴロゴロレポート",
                        "description": (
                            "昨日のデータが見つかりませんでしたわ...\n"
                            "カメラがお休みだったのかしら？"
                        ),
                        "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                    }
                ],
            )
            return

        points = [
            {
                "timestamp": datetime.fromisoformat(record["timestamp"]["S"]),  # type: ignore
                "is_in_bed": record["is_in_bed"]["BOOL"],  # type: ignore
            }
            for record in records
        ]
        df = pd.DataFrame(points).sort_values("timestamp")

        in_bed_rate = self._calc_in_bed_rate(df)

        count_b = df["is_in_bed"].sum()
        count_t = len(df)

        match in_bed_rate:
            case r if r < 20:
                label = "とっても活動的"
            case r if r < 40:
                label = "まあまあ活動的"
            case r if r < 60:
                label = "ちょっとゴロゴロ"
            case r if r < 80:
                label = "かなりゴロゴロ"
            case _:
                label = "究極のゴロゴロ"

        hours_b, mins_b = divmod(count_b * 5, 60)
        hours_t, mins_t = divmod(count_t * 5, 60)

        filled = round(in_bed_rate / 5)
        progress_bar = "▓" * filled + "░" * (20 - filled) + f"  {in_bed_rate:.1f}%"

        chart_image = self._render_chart(df)

        agent = SalomeLazinessAgent()
        result = agent.run(
            summary=(
                f"日付: {yesterday.strftime('%Y-%m-%d')}\n"
                f"ゴロゴロ度: {in_bed_rate:.1f}% ({label})\n"
                f"ベッド滞在時間: {hours_b}時間{mins_b}分 / 監視時間: {hours_t}時間{mins_t}分"
            ),
            chart_image=chart_image,
        )
        comment = result.comment

        self.bot.client.send_channel_message(
            channel_id=self.channel_id,
            embeds=[
                {
                    "title": f"🛏️ 昨日のゴロゴロレポート ({yesterday.strftime('%Y-%m-%d')})",
                    "description": (
                        f"昨日のゴロゴロ度は **{in_bed_rate:.1f}%**({label}) ですわ！\n{comment}"
                    ),
                    "fields": [
                        {
                            "name": "🕐 ベッドにいた時間",
                            "value": (
                                f"{hours_b}時間{mins_b}分 / {hours_t}時間{mins_t}分"
                            ),
                            "inline": False,
                        },
                        {
                            "name": "📊 ゴロゴロ度",
                            "value": progress_bar,
                            "inline": False,
                        },
                    ],
                    "image": {"url": "attachment://laziness.png"},
                    "color": Config.DEFAULT_DISCORD_EMBED_COLOR,
                }
            ],
            files=[("laziness.png", chart_image)],
        )

    def _calc_in_bed_rate(self, df: pd.DataFrame) -> float:
        is_evening = df["timestamp"].dt.hour >= 18

        day_mean = df.loc[~is_evening, "is_in_bed"].mean()
        day_rate = day_mean * 100 if (~is_evening).any() else 0

        evening_mean = df.loc[is_evening, "is_in_bed"].mean()
        evening_rate = evening_mean * 100 if is_evening.any() else 0

        return min(day_rate * 0.3 + evening_rate * 0.9, 100)

    def _render_chart(self, df: pd.DataFrame) -> bytes:
        fig, ax = plt.subplots(figsize=(10, 2))

        ax.fill_between(
            df["timestamp"],
            df["is_in_bed"].astype(int),
            step="post",
            alpha=0.7,
            color="#743D90",
        )
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["Active", "In Bed"])
        ax.set_xlim(df["timestamp"].min(), df["timestamp"].max())
        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%H:%M", tz=ZoneInfo("Asia/Tokyo"))
        )

        fig.tight_layout()

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=150)
        plt.close(fig)

        return buffer.getvalue()
