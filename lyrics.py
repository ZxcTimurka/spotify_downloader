import os
from pathlib import Path
import syncedlyrics
import ui


class LyricsFetcher:
    def __init__(self):
        pass

    def is_active(self) -> bool:
        return True

    def fetch_lyrics(self, track_name: str, artist_name: str, output_dir: Path) -> bool:
        try:
            search_query = f"{artist_name} {track_name}"
            
            file_name = f"{artist_name} - {track_name}.lrc"
            file_name = "".join(c for c in file_name if c.isalnum() or c in (' ', '-', '.'))
            file_path = output_dir / file_name

            if file_path.exists():
                ui.log(f"  [bold green]Текст для '{track_name}' уже существует (кешировано).[/bold green]")
                return True

            ui.log(f"  [dim]Ищу текст с syncedlyrics для '{search_query}'[/dim]")
            lyrics_text = syncedlyrics.search(search_query)
            if lyrics_text:
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
