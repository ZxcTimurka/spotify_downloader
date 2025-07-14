
Модуль для работы с API Genius для поиска и сохранения текстов песен.


import os
import re
from pathlib import Path

import lyricsgenius
from dotenv import load_dotenv
from rich.console import Console

# Загружаем переменные окружения (для токена API)
load_dotenv()

console = Console()


def clean_filename(filename: str) -> str:
    """
    Очищает имя файла от недопустимых символов.
    """
    return re.sub(r'[\\/*?:"<>|]', "", filename)


class LyricsFetcher:
    """
    Класс для получения текстов песен с Genius.
    """

    def __init__(self):
        self.genius_token = os.getenv("GENIUS_ACCESS_TOKEN")
        self.genius_api = self._initialize_api()

    def _initialize_api(self):
        """Инициализирует API, если токен доступен."""
        if self.genius_token and self.genius_token != "YOUR_TOKEN_HERE":
            try:
                return lyricsgenius.Genius(self.genius_token, verbose=False, remove_section_headers=True)
            except Exception as e:
                console.print(f"[bold red]Ошибка инициализации LyricsGenius: {e}[/bold red]")
                return None
        return None

    def is_active(self) -> bool:
        """Проверяет, активен ли API клиент."""
        return self.genius_api is not None

    def fetch_lyrics(self, track_name: str, artist_name: str, output_dir: Path) -> bool:
        """
        Ищет, получает и сохраняет текст песни.

        Args:
            track_name (str): Название трека.
            artist_name (str): Имя исполнителя.
            output_dir (Path): Директория для сохранения файла.

        Returns:
            bool: True, если текст успешно найден и сохранен, иначе False.
        """
        if not self.is_active():
            return False

        try:
            song = self.genius_api.search_song(track_name, artist_name)
            if song and song.lyrics:
                # Удаляем первую строку с "Embed" и последнюю с "Embed"
                lyrics_lines = song.lyrics.split('\n')
                if "Embed" in lyrics_lines[-1]:
                    lyrics_lines.pop(-1)
                if lyrics_lines and "Embed" in lyrics_lines[0]:
                     lyrics_lines.pop(0)
                
                lyrics_text = "\n".join(lyrics_lines).strip()

                # Genius может добавлять "Contributors" в конец, убираем это
                lyrics_text = re.sub(r'\d*Contributors.*', '', lyrics_text).strip()


                if not lyrics_text:
                    return False

                # Создаем имя файла в формате .lrc, но сохраняем как .txt,
                # так как Genius не предоставляет синхронизированный формат.
                # Это компромисс, чтобы иметь файл с правильным расширением для плееров,
                # которые могут отображать и несинхронизированные .lrc.
                file_name = clean_filename(f"{artist_name} - {track_name}.lrc")
                file_path = output_dir / file_name

                file_path.write_text(lyrics_text, encoding="utf-8")
                return True
        except Exception:
            # Игнорируем ошибки, если песня или текст не найдены
            return False
        
        return False
