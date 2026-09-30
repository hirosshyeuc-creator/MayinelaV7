import re
from telethon import events
from .client import client
from .config import settings
from .registry import COMMANDS
from .database import db

_INSTALLED = False

def install_dispatcher():
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    @client.on(events.NewMessage(outgoing=True))
    async def handler(event):
        text = event.raw_text or ""
        if not text.startswith(settings.prefix):
            return
        match = re.match(rf"^{re.escape(settings.prefix)}([A-Za-z0-9_]+)(?:\s+(.*))?$", text, re.S)
        if not match:
            return
        cmd = match.group(1).lower()
        args = (match.group(2) or "").strip()
        func = COMMANDS.get(cmd)
        if not func:
            return
        meta = getattr(func, "_mayinela", {})
        if meta.get("owner") and event.sender_id != settings.owner_id:
            await event.edit("⛔ Este comando está restringido al propietario.")
            return
        await db.inc(cmd)
        try:
            await func(event, args)
        except Exception as exc:
            try:
                await event.edit(f"❌ Error en `{cmd}`: {type(exc).__name__}: {exc}")
            except Exception:
                pass
