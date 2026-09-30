import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    api_id: int
    api_hash: str
    phone: str
    owner_id: int
    prefix: str
    session_name: str
    db_path: str
    log_level: str

def _int(name, default="0"):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return int(default)

settings = Settings(
    api_id=_int("API_ID"),
    api_hash=os.getenv("API_HASH", ""),
    phone=os.getenv("PHONE", ""),
    owner_id=_int("OWNER_ID"),
    # PREFIX is reserved by Termux/Android. Use MAYINELA_PREFIX instead.
    prefix=os.getenv("MAYINELA_PREFIX", os.getenv("PREFIX") if os.getenv("PREFIX") in {".", "!", "/", "#", "$", ">", "~"} else "."),
    session_name=os.getenv("SESSION_NAME", "mayinela"),
    db_path=os.getenv("DB_PATH", "data/mayinela.db"),
    log_level=os.getenv("LOG_LEVEL", "INFO"),
)

if not settings.api_id or not settings.api_hash:
    raise RuntimeError("Faltan API_ID/API_HASH en .env")
