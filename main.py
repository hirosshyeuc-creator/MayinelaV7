import asyncio
import logging
from pathlib import Path

from mayinela.core.config import settings
from mayinela.core.client import client
from mayinela.core.loader import load_plugins
from mayinela.core.dispatch import install_dispatcher
from mayinela.core.database import db

Path("logs").mkdir(parents=True, exist_ok=True)
Path("sessions").mkdir(parents=True, exist_ok=True)
Path("data").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/mayinela.log", encoding="utf-8")],
)
log = logging.getLogger("mayinela")

async def main():
    await db.init()
    await load_plugins()
    install_dispatcher()
    await client.start(phone=settings.phone or None)
    me = await client.get_me()
    log.info("Mayinela conectada como %s (%s)", getattr(me, "username", None), me.id)
    print(f"Mayinela está activa. Usa {settings.prefix}menu")
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Mayinela detenida.")
