# 🎵 Spotify Downloader CLI 🎵

Это полнофункциональное консольное приложение для массового скачивания треков, альбомов и плейлистов из Spotify.

## ✨ Возможности

- **Массовая загрузка**: Скачивайте треки по списку из `.txt` файла.
- **Высокое качество**: Загрузка аудио в наилучшем доступном качестве с помощью `spotdl`.
- **Метаданные**: Автоматическое встраивание обложек альбомов, названий, исполнителей и т.д.
- **Тексты песен**: Попытка найти и сохранить тексты песен в формате `.lrc` (как `.txt` файл).
- **Красивый интерфейс**: Интерактивный TUI с прогресс-барами и логами на базе `rich`.
- **Удобный CLI**: Понятный интерфейс командной строки на базе `typer`.
- **Кроссплатформенность**: Работает на Windows, macOS и Linux.

## ⚙️ Установка

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/ZxcTimurka/spotify_downloader.git
    cd spotify-downloader
    ```

2.  **Создайте виртуальное окружение (рекомендуется):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Linux/macOS
    # venv\Scripts\activate    # Для Windows
    ```

3.  **Установите зависимости:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Установите FFmpeg:**
    Для встраивания метаданных и конвертации `spotdl` требует `FFmpeg`. Убедитесь, что он установлен и доступен в системной переменной `PATH`.
    - **Windows**: Скачайте с [официального сайта](https://ffmpeg.org/download.html) и добавьте путь к `bin` в `PATH`.
    - **macOS**: `brew install ffmpeg`
    - **Linux**: `sudo apt update && sudo apt install ffmpeg`

5.  **(Опционально) Настройка для загрузки текстов песен:**
    Чтобы скачивать тексты, вам нужен API-ключ от **Genius**.
    - Перейдите на [Genius API Clients](https://genius.com/api-clients) и создайте ново��о клиента, чтобы получить `Access Token`.
    - Скопируйте файл `.env.example` в новый файл с именем `.env`:
      ```bash
      cp .env.example .env
      ```
    - Откройте `.env` и вставьте ваш токен вместо `"YOUR_TOKEN_HERE"`:
      ```
      GENIUS_ACCESS_TOKEN="ВАШ-СУПЕР-СЕКРЕТНЫЙ-ТОКЕН"
      ```
    Если вы не выполните этот шаг, загрузка текстов будет автоматически пропущена.

## 🚀 Использование

Основная команда для запуска приложения — `python main.py`.

### Аргументы

- `--input` / `-i`: **(Обязательный)** Путь к вашему `.txt` файлу. В файле каждая новая строка - это новый запрос для поиска (название трека, ссылка на альбом или плейлист).
- `--output` / `-o`: **(Обязательный)** Путь к папке, куда будут сохраняться треки.
- `--lyrics` / `--no-lyrics`: Включить или отключить загрузку текстов. По умолчанию включена.

### Пример файла `songs.txt`

```
Daft Punk - Around the World
https://open.spotify.com/album/4tBQifX2ma1SABkI5M5v7v
Gorillaz - Feel Good Inc
Queen - Bohemian Rhapsody
```

### Пример команды

```bash
python main.py --input songs.txt --output ./МояМузыка --lyrics
```

Или с отключенными текстами:

```bash
python main.py -i C:\Users\User\Desktop\songs.txt -o D:\Music --no-lyrics
```
