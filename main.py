import sys
from pathlib import Path
from typing_extensions import Annotated

import typer

import ui
from downloader import SpotifyDownloader

app = typer.Typer(
    name="spotify-downloader",
    help="🎵 Утилита для массовой загрузки треков из Spotify по списку из .txt файла.",
    add_completion=False,
)


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
    output_dir.mkdir(parents=True, exist_ok=True)

    ui.print_header()

    try:
        downloader = SpotifyDownloader(
            output_dir=output_dir,
            download_lyrics=lyrics,
        )
        downloader.download_from_list(input_file)
        summary = downloader.get_summary()
    except Exception as e:
        ui.log(f"\n[bold red]Произошла критическая ошибка:[/bold red] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    ui.print_summary(summary)


if __name__ == "__main__":
    app()
