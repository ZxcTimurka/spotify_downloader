"""
Модуль для управления и отображения пользовательского интерфейса в терминале
с использованием библиотеки rich.
"""

from rich.console import Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.rule import Rule
from rich.text import Text

# Настройка прогресс-бара для отдельных треков
task_progress = Progress(
    TextColumn("[bold blue]├─ {task.description}", justify="left"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    TimeRemainingColumn(),
    expand=True,
)

# Настройка прогресс-бара для общего процесса
overall_progress = Progress(
    TextColumn("[bold green]└─ {task.description}", justify="left"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    expand=True,
)

# Группа для отображения прогресс-баров вместе
progress_group = Group(task_progress, overall_progress)

# Панель для логов
log_panel = Panel(
    "",
    title="[bold yellow]Лог операций[/bold yellow]",
    border_style="yellow",
    expand=True,
    padding=(1, 2),
)


def create_layout() -> Layout:
    """Создает и возвращает структуру интерфейса."""
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=3),
        Layout(ratio=1, name="main"),
        Layout(size=5, name="footer"),
    )

    layout["header"].update(
        Panel(
            Text("🎵 Spotify Downloader 🎵", justify="center", style="bold magenta"),
            border_style="magenta",
        )
    )
    layout["main"].update(
        Panel(
            progress_group,
            title="[bold green]Прогресс загрузки[/bold green]",
            border_style="green",
        )
    )
    layout["footer"].update(log_panel)
    return layout


class UIManager:
    """
    Класс для управления Live-интерфейсом Rich.
    """

    def __init__(self):
        self.layout = create_layout()
        self.live = Live(self.layout, screen=True, redirect_stderr=False)
        self._log_messages = []

    def __enter__(self):
        self.live.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.live.stop()

    def add_log_message(self, message: str):
        """Добавляет сообщение в лог-панель."""
        self._log_messages.append(message)
        # Оставляем только последние 10 сообщений, чтобы не переполнять панель
        if len(self._log_messages) > 10:
            self._log_messages.pop(0)
        
        log_panel.renderable = "\n".join(self._log_messages)
        self.live.refresh()

    def update_task_progress(self, total: int):
        """Создает и возвращает задачу для прогресс-бара треков."""
        return task_progress.add_task("Скачивание треков...", total=total)

    def update_overall_progress(self, total: int):
        """Создает и возвращает задачу для общего прогресс-бара."""
        return overall_progress.add_task("Общий прогресс", total=total)

    def advance_progress(self, task_id, overall_id):
        """Продвигает прогресс-бары."""
        task_progress.update(task_id, advance=1)
        overall_progress.update(overall_id, advance=1)

