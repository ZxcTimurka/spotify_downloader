"""
Модуль для работы с API Genius для поиска и сохранения текстов песен.
"""

import os
from pathlib import Path

import syncedlyrics

import ui


class LyricsFetcher:
    """
    Класс для получения текстов песен с syncedlyrics.
    """

    def __init__(self):
        # syncedlyrics does not require explicit API initialization or tokens
        # for basic search, so we can simplify this.
        pass

    def is_active(self) -> bool:
        """
        syncedlyrics is always active as it doesn't rely on external tokens.
        """
        return True

    def fetch_lyrics(self, track_name: str, artist_name: str, output_dir: Path) -> bool:
        """
        Ищет, получает и сохраняет текст песни, используя syncedlyrics.
        """
        try:
            search_query = f"{artist_name} {track_name}"
            
            # Create a clean filename for caching check
            file_name = f"{artist_name} - {track_name}.lrc"
            file_name = "".join(c for c in file_name if c.isalnum() or c in (' ', '-', '.'))
            file_path = output_dir / file_name

            # Check if lyric file already exists
            if file_path.exists():
                ui.log(f"  [bold green]Текст для '{track_name}' уже существует (кешировано).[/bold green]")
                return True

            ui.log(f"  [dim]Ищу текст с syncedlyrics для '{search_query}'[/dim]")

            # Use syncedlyrics to search for lyrics
            lyrics_text = syncedlyrics.search(search_query)

            if lyrics_text:
                
                # Ensure output directory exists
                output_dir.mkdir(parents=True, exist_ok=True)

                file_path.write_text(lyrics_text, encoding="utf-8")
                ui.log(f"  [bold green]Текст успешно сохранен в {file_path.name}[/bold green]")
                return True
            else:
                ui.log(f"  [yellow]Текст для '{search_query}' не найден с syncedlyrics.[/yellow]")
                return False

        except Exception as e:
            ui.log(f"  [red]Произошла ошибка при поиске текста с syncedlyrics: {e}[/red]")
            return False
