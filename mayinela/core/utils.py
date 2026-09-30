import time
from telethon.tl.types import User, Chat, Channel

START_TIME = time.time()

def fmt_uptime(seconds):
    seconds = int(seconds)
    d, seconds = divmod(seconds, 86400)
    h, seconds = divmod(seconds, 3600)
    m, s = divmod(seconds, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)

def entity_name(entity):
    if isinstance(entity, User):
        return " ".join(x for x in [entity.first_name, entity.last_name] if x) or "Usuario"
    if isinstance(entity, (Chat, Channel)):
        return getattr(entity, "title", None) or "Chat"
    return str(entity)
