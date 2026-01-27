import questionary
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from salome.agents import SalomeRecipeAgent

console = Console()


if __name__ == "__main__":
    console.print("🍳 Salome Recipe Agent", style="bold cyan")

    order = questionary.text("指示を入力してください:").ask()

    if not order:
        console.print("❌ 指示が入力されていません", style="bold red")
        exit(1)

    debug = questionary.confirm("デバッグモードを有効にしますか?", default=False).ask()

    agent = SalomeRecipeAgent()
    result = agent.run(order, debug)

    console.print(
        Panel(
            Markdown(result.answer),
            title="💬 回答",
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
