import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from salome.agents import SalomeAskAgent

console = Console()


if __name__ == "__main__":
    console.print("✨ Salome Ask Agent", style="bold cyan")

    question = questionary.text("質問を入力してください:").ask()

    if not question:
        console.print("❌ 質問が入力されていません", style="bold red")
        exit(1)

    with console.status("[cyan]回答を生成中...[/cyan]", spinner="dots"):
        agent = SalomeAskAgent()
        result = agent.run(question)

    console.print(
        Panel(
            result.answer,
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
