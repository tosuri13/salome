import io
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import questionary
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from salome.agents import SalomeLazinessAgent
from salome.utils.aws import DynamoDBClient

console = Console()

TABLE_NAME = os.environ["LAZYCAM_RECORDS_TABLE_NAME"]


if __name__ == "__main__":
    console.print("🛏️ Salome Laziness Agent", style="bold cyan")

    today = datetime.now(ZoneInfo("Asia/Tokyo"))
    choices = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 4)]
    target_date = questionary.select(
        "対象の日付を選択してください:",
        choices=choices,
    ).ask()

    if not target_date:
        console.print("❌ 日付が選択されていません", style="bold red")
        exit(1)

    console.print(f"📥 {target_date} のデータを取得中...", style="yellow")

    dynamodb = DynamoDBClient()
    response = dynamodb.query(
        TableName=TABLE_NAME,
        KeyConditionExpression="#d = :date",
        ExpressionAttributeNames={"#d": "date"},
        ExpressionAttributeValues={":date": {"S": target_date}},
    )
    records = response["Items"]

    if not records:
        console.print("❌ データが見つかりませんでした", style="bold red")
        exit(1)

    console.print(f"📊 {len(records)} 件のレコードを取得しました", style="green")

    points = [
        {
            "timestamp": datetime.fromisoformat(record["timestamp"]["S"]),  # type: ignore
            "is_in_bed": record["is_in_bed"]["BOOL"],  # type: ignore
        }
        for record in records
    ]
    df = pd.DataFrame(points).sort_values("timestamp")

    is_evening = df["timestamp"].dt.hour >= 18
    day_rate = df.loc[~is_evening, "is_in_bed"].mean() * 100 if (~is_evening).any() else 0
    evening_rate = df.loc[is_evening, "is_in_bed"].mean() * 100 if is_evening.any() else 0
    in_bed_rate = min(evening_rate * 0.9 + day_rate * 0.3, 100)

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

    console.print(
        Panel(
            f"ゴロゴロ度: {in_bed_rate:.1f}% ({label})\n"
            f"ベッド滞在: {hours_b}時間{mins_b}分 / {hours_t}時間{mins_t}分",
            title=f"📊 {target_date} の集計",
            border_style="cyan",
        )
    )

    console.print("📈 チャートを生成中...", style="yellow")

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

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    chart_image = buf.getvalue()

    console.print("🤖 AIがコメントを生成中...", style="yellow")

    agent = SalomeLazinessAgent()
    result = agent.run(
        summary=(
            f"日付: {target_date}\n"
            f"ゴロゴロ度: {in_bed_rate:.1f}% ({label})\n"
            f"ベッド滞在時間: {hours_b}時間{mins_b}分 / 監視時間: {hours_t}時間{mins_t}分"
        ),
        chart_image=chart_image,
    )

    console.print(
        Panel(
            Markdown(result.comment),
            title="💬 AIによるコメント",
            border_style="green",
        )
    )

    table = Table(title="📊 使用量メトリクス")
    table.add_column("項目", style="cyan")
    table.add_column("値", style="green", justify="right")
    table.add_row("Input Tokens", str(result.usage["inputTokens"]))
    table.add_row("Output Tokens", str(result.usage["outputTokens"]))
    table.add_row("Total Tokens", str(result.usage["totalTokens"]))

    console.print(table)

    console.print("📈 チャートを表示中... (ウィンドウを閉じると終了)", style="green")
    plt.show()
