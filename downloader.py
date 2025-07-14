
"""
Основной модуль, отвечающий за логику загрузки треков.
"""

import os
import logging
from pathlib import Path
from datetime import timedelta

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotdl import Spotdl
from dotenv import load_dotenv


import ui
from lyrics import LyricsFetcher

# Загружаем переменные окружения из .env файла
load_dotenv()


class SpotifyDownloader:
    """
    Класс-оркестратор для процесса загрузки.
    """

    def __init__(self, output_dir: Path, download_lyrics: bool):
        self.output_dir = output_dir
        self.download_lyrics = download_lyrics
        self.lyrics_fetcher = LyricsFetcher() if download_lyrics else None
        self.match_threshold = 90  # Общий порог схожести, используется для запросов без исполнителя

        # Настройка SpotDL
        downloader_settings = {
            "output": str(self.output_dir / "{artist} - {title}.{output-ext}"),
            "ffmpeg": "ffmpeg",
            "bitrate": "320k",
            "threads": 4,
        }
        
        self.spotdl_client = Spotdl(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            downloader_settings=downloader_settings,
        )

        self.spotify_client = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
            )
        )
        
        self.stats = {
            "success": 0,
            "failed": 0,
            "total_duration_ms": 0,
        }

    def download_from_list(self, file_path: Path):
        """
        Загружает треки из текстового файла, обрабатывая каждый запрос поочередно.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                queries = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            ui.log(f"[bold red]Ошибка: Файл не найден по пути {file_path}[/bold red]")
            return

        if not queries:
            ui.log("[bold yellow]Предупреждение: Входной файл пуст.[/bold yellow]")
            return

        total_queries = len(queries)
        ui.log(f"Найдено {total_queries} запросов. Начинаю поочередную обработку...")

        for i, query in enumerate(queries, 1):
            ui.log(f"\n[bold]({i}/{total_queries})[/bold] 🔍 Ищу трек по запросу: [cyan]'{query}'[/cyan]")

            spotify_track_url = None
            query_parts = query.rsplit(" - ", 1)
            
            if len(query_parts) == 2:
                artist_query, track_query = query_parts
                search_q = f"track:{track_query} artist:{artist_query}"
            else:
                search_q = f"track:{query}"

            try:
                results = self.spotify_client.search(q=search_q, type='track', limit=1)
                if results and results['tracks']['items']:
                    spotify_track_url = results['tracks']['items'][0]['external_urls']['spotify']
                    track_name = results['tracks']['items'][0]['name']
                    track_artists = ", ".join([artist['name'] for artist in results['tracks']['items'][0]['artists']])
                    ui.log(f"✅ Трек найден на Spotify: [green]'{track_name} - {track_artists}'[/green].")
                else:
                    ui.log(f"❌ Трек по запросу '[yellow]{query}[/yellow]' не найден на Spotify.")
                    self.stats["failed"] += 1
                    continue
            except Exception as e:
                ui.log(f"❌ Ошибка при поиске трека на Spotify для запроса '[yellow]{query}[/yellow]': {e}")
                self.stats["failed"] += 1
                continue

            # Get the Song object from spotdl using the Spotify URL
            spotdl_song_list = self.spotdl_client.search([spotify_track_url])
            
            if not spotdl_song_list:
                ui.log(f"❌ SpotDL не смог найти трек по URL: [yellow]{spotify_track_url}[/yellow]. Пропускаю.")
                self.stats["failed"] += 1
                continue
            
            song_to_download = spotdl_song_list[0] # Take the first (and likely only) result
            
            download_results = self.spotdl_client.download_songs([song_to_download])
            downloaded_song, path = download_results[0] if download_results else (None, None)

            if path:
                self.stats["success"] += 1
                self.stats["total_duration_ms"] += (downloaded_song.duration * 1000)
                ui.log(f"✅ Трек [green]'{downloaded_song.name}'[/green] успешно скачан.")

                lyrics_output_dir = self.output_dir / "lyrics"
                lyrics_output_dir.mkdir(exist_ok=True)

                if self.download_lyrics and self.lyrics_fetcher:
                    if not self.lyrics_fetcher.is_active():
                        ui.log("[yellow]Токен Genius API не найден. Пропускаю загрузку текстов.[/yellow]")
                        self.download_lyrics = False
                    else:
                        ui.log(f"📄 Ищу текст для: [cyan]{downloaded_song.name}[/cyan]")
                        lyrics_found = self.lyrics_fetcher.fetch_lyrics(
                            track_name=downloaded_song.name,
                            artist_name=downloaded_song.artist,
                            output_dir=lyrics_output_dir
                        )
                        if lyrics_found:
                            ui.log(f"📄 Текст для [green]{downloaded_song.name}[/green] успешно сохранен.")
                        else:
                            ui.log(f"⚠️  Текст для [yellow]{downloaded_song.name}[/yellow] не найден.")
            else:
                self.stats["failed"] += 1
                ui.log(f"❌ Не удалось скачать трек: [red]'{song_to_download.name} - {song_to_download.artist}'[/red]")

        ui.log("\n[bold green]Обработка всех запросов завершена![/bold green]")

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
