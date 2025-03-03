# Convertio Telegram Bot

A Telegram bot that allows users to convert files between different formats using the Convertio API. This bot makes file conversion simple and accessible directly through Telegram.

## Features

- Convert files between various formats
- Support for documents, images, audio, video, and more
- Simple user interface with button selection for common formats
- Custom format input for less common conversions
- Real-time conversion status updates
- Direct delivery of converted files

## Supported Formats

The bot supports all formats available through the Convertio API, including:

- **Documents**: PDF, DOCX, DOC, ODT, RTF, TXT
- **Images**: JPG, PNG, GIF, BMP, TIFF, SVG
- **Audio**: MP3, WAV, OGG, FLAC, AAC
- **Video**: MP4, AVI, MOV, MKV, WEBM
- **Archives**: ZIP, RAR, 7Z, TAR

And many more. For a complete list, visit [Convertio Formats](https://convertio.co/formats/).

## Prerequisites

- Python 3.7 or higher
- A Telegram account
- A Convertio API key (Get one at [Convertio](https://convertio.co/api/))
- A Telegram Bot Token (Create one via [BotFather](https://t.me/BotFather))

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/thebrainair/Converter-tg-bot.git
cd Converter-tg-bot
```

### 2. Set up a virtual environment (recommended)

For macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

For Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install python-telegram-bot requests
```

Or using requirements.txt:

```bash
pip install -r requirements.txt
```

### 4. Configure the bot

Open `bot.py` and replace the placeholders with your actual credentials:

```python
API_KEY = "YOUR_CONVERTIO_API_KEY"  # Replace with your Convertio API key
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # Replace with your Telegram bot token
```

## Running the Bot

With the virtual environment activated, run:

```bash
python bot.py
```

The bot will start and be available on Telegram.

## Usage

1. Start a chat with your bot on Telegram
2. Use the `/start` command to initialize the bot
3. Send any file you want to convert
4. Select the output format from the provided buttons or enter a custom format
5. Wait for the conversion to complete
6. Download your converted file

## Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/formats` - Show available output formats

## Limitations

- File size limitations are determined by both Telegram (up to 50MB) and Convertio API (depends on your plan)
- Conversion time depends on file size, format, and Convertio server load
- You need a valid Convertio API key with sufficient credits

## Error Handling

The bot provides user-friendly error messages for:

- Invalid file formats
- Failed conversions
- API errors
- Network issues

## Acknowledgments

- [Convertio](https://convertio.co/) for providing the conversion API
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the Telegram Bot API wrapper
