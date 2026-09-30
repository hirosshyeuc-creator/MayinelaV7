from telethon import TelegramClient
from .config import settings

client = TelegramClient(
    f"sessions/{settings.session_name}",
    settings.api_id,
    settings.api_hash,
)
