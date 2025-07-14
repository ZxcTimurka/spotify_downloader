"""
Модуль для управления и отображения пользовательского интерфейса в терминале
с использованием библиотеки rich.

Этот модуль предоставляет простые функции для вывода сообщений, так как
основной UI для прогресса загрузки обрабатывается самой библиотекой spotdl.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def print_header():
    """Выводит заголовок приложения."""
    console.print(
        Panel(
            Text("🎵 Spotify Downloader 🎵", justify="center", style="bold magenta"),
            border_style="magenta",
        )
    )


def log(message: str):
    """Выводит лог-сообщение в консоль."""
    console.print(message)


def print_summary(summary: dict):
    """Выводит итоговую сводку по результатам работы."""
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