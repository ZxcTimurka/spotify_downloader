"""
Основной модуль, отвечающий за логику загрузки треков.
"""

import time
from pathlib import Path
from datetime import timedelta

from spotdl import Spotdl
from spotdl.types.song import Song

from ui import UIManager
from lyrics import LyricsFetcher


class SpotifyDownloader:
    """
    Класс-оркестратор для процесса загрузки.
    """

    def __init__(self, output_dir: Path, download_lyrics: bool, ui: UIManager):
        self.output_dir = output_dir
        self.download_lyrics = download_lyrics
        self.ui = ui
        self.lyrics_fetcher = LyricsFetcher() if download_lyrics else None

        # Настройка SpotDL
        self.spotdl_client = Spotdl(
            client_id="YOUR_SPOTIFY_CLIENT_ID", # SpotDL использует анонимный аккаунт, если это не указано
            client_secret="YOUR_SPOTIFY_CLIENT_SECRET",
            output=str(self.output_dir / "{artist} - {title}.{output-ext}"),
            ffmpeg="ffmpeg",  # Убедитесь, что ffmpeg в PATH
            bitrate="best",
            preload=False,
            threads=4,
            log_level="ERROR",
        )
        
        self.stats = {
            "success": 0,
            "failed": 0,
            "total_duration_ms": 0,
        }

    def download_from_list(self, file_path: Path):
        """
        Загружает треки из текстового файла.

        Args:
            file_path (Path): Путь к .txt файлу со списком треков.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                queries = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.ui.add_log_message(f"[bold red]Ошибка: Файл не найден по пути {file_path}[/bold red]")
            return

        if not queries:
            self.ui.add_log_message("[bold yellow]Предупреждение: Входной файл пуст.[/bold yellow]")
            return

        self.ui.add_log_message(f"Найдено {len(queries)} запросов. Начинаю поиск...")
        
        # Ищем все песни сразу для эффективности
        songs = self.spotdl_client.search(queries)
        
        # Фильтруем ненайденные треки
        found_songs = [song for song in songs if song is not None]
        self.stats["failed"] = len(songs) - len(found_songs)

        if not found_songs:
            self.ui.add_log_message("[bold red]Не удалось найти ни одного трека по вашим запросам.[/bold red]")
            return

        self.ui.add_log_message(f"Найдено {len(found_songs)} треков. Начинаю загрузку...")
        time.sleep(1) # Небольшая пауза для чтения лога

        task_id = self.ui.update_task_progress(total=len(found_songs))
        overall_id = self.ui.update_overall_progress(total=len(found_songs))

        for song in found_songs:
            self.process_song(song)
            self.ui.advance_progress(task_id, overall_id)
        
        self.ui.add_log_message("[bold green]Загрузка завершена![/bold green]")

    def process_song(self, song: Song):
        """
        Обрабатывает один трек: скачивает, получает текст.
        """
        self.ui.add_log_message(f"⬇️  Скачиваю: [cyan]{song.name} - {song.artist}[/cyan]")
        
        # Скачиваем трек
        results = self.spotdl_client.download(song)
        
        if results and results[0] and results[0][1]: # Проверяем успешность загрузки
            downloaded_song_path = Path(results[0][1])
            self.stats["success"] += 1
            self.stats["total_duration_ms"] += song.duration_ms
            self.ui.add_log_message(f"✅  Успешно скачан: [green]{song.name}[/green]")

            # Скачиваем текст, если опция включена
            if self.download_lyrics and self.lyrics_fetcher:
                if not self.lyrics_fetcher.is_active():
                    self.ui.add_log_message("[yellow]Токен Genius API не найден. Пропускаю загрузку текстов.[/yellow]")
                    self.download_lyrics = False # Отключаем для последующих треков
                    return

                self.ui.add_log_message(f"📄  Ищу текст для: [cyan]{song.name}[/cyan]")
                lyrics_found = self.lyrics_fetcher.fetch_lyrics(
                    track_name=song.name,
                    artist_name=song.artist,
                    output_dir=downloaded_song_path.parent
                )
                if lyrics_found:
                    self.ui.add_log_message(f"📄  Текст для [green]{song.name}[/green] успешно сохранен.")
                else:
                    self.ui.add_log_message(f"⚠️  Текст для [yellow]{song.name}[/yellow] не найден.")
        else:
            self.stats["failed"] += 1
            self.ui.add_log_message(f"❌  Не удалось скачать: [red]{song.name} - {song.artist}[/red]")

    def get_summary(self) -> dict:
        """
        Возвращает итоговую статистику.
        """
        total_duration = str(timedelta(milliseconds=self.stats["total_duration_ms"]))
        return {
            "success": self.stats["success"],
            "failed": self.stats["failed"],
            "total_duration": total_duration,
        }
