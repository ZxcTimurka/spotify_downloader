from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def print_header():
    console.print(
        Panel(
            Text("🎵 Spotify Downloader 🎵", justify="center", style="bold magenta"),
            border_style="magenta",
        )
    )


def log(message: str):
    console.print(message)


def print_summary(summary: dict):
    summary_text = Text(justify="left")
    summary_text.append(f"✅ Успешно скачано: {summary['success']}\n", style="green")
    summary_text.append(f"❌ Не удалось: {summary['failed']}\n", style="red")
    summary_text.append(f"⏱️ Общая длительность: {summary['total_duration']}", style="blue")

    console.print(
        Panel(
            summary_text,
            title="[bold yellow]Итоги сессии[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
            expand=False,
        )
    )
