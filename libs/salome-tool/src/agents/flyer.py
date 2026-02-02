import questionary
import requests
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from salome.agents import SalomeFlyerAgent

console = Console()


if __name__ == "__main__":
    console.print("🛒 Salome Flyer Agent", style="bold cyan")

    url = questionary.text("チラシのURLを入力してください:").ask()

    if not url:
        console.print("❌ URLが入力されていません", style="bold red")
        exit(1)

    debug = questionary.confirm("デバッグモードを有効にしますか?", default=False).ask()

    console.print("📥 チラシをダウンロード中...", style="yellow")
    content = requests.get(url).content

    console.print("🤖 AIがチラシを分析中...", style="yellow")
    agent = SalomeFlyerAgent()
    result = agent.run(content, debug)

    console.print(
        Panel(
            Markdown(result.summary),
            title="📋 チラシのサマリー",
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
