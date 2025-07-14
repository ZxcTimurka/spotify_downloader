
"""
Главный файл для запуска CLI-приложения Spotify Downloader.
Использует Typer для обработки аргументов командной строки.
"""

import sys
from pathlib import Path
from typing_extensions import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from downloader import SpotifyDownloader
from ui import UIManager

# Создаем экземпляр Typer
app = typer.Typer(
    name="spotify-downloader",
    help="🎵 Утилита для массовой загрузки треков из Spotify по списку из .txt файла.",
    add_completion=False,
)

console = Console()


@app.command(
    epilog="Пример: python main.py --input songs.txt --output ./Music --lyrics"
)
def main(
    input_file: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            help="Путь к .txt файлу со списком треков/альбомов/плейлистов.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Директория для сохранения скачанных треков.",
            file_okay=False,
            dir_okay=True,
            writable=True,
            resolve_path=True,
        ),
    ],
    lyrics: Annotated[
        bool,
        typer.Option(
            "--lyrics/--no-lyrics",
            "-l/-nl",
            help="Включить/отключить загрузку текстов песен.",
        ),
    ] = True,
):
    """
    Основная функция, запускающая процесс загрузки.
    """
    # Создаем директорию, если она не существует
    output_dir.mkdir(parents=True, exist_ok=True)

    # Запускаем UI менеджер
    with UIManager() as ui:
        try:
            downloader = SpotifyDownloader(
                output_dir=output_dir,
                download_lyrics=lyrics,
                ui=ui,
            )
            downloader.download_from_list(input_file)
            summary = downloader.get_summary()
        except Exception as e:
            ui.live.stop()
            console.print(f"\n[bold red]Произошла критическая ошибка:[/bold red] {e}")
            sys.exit(1)

    # Выводим финальную сводку
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


if __name__ == "__main__":
    app()

