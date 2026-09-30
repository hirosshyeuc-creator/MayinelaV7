import os
import platform
import time
import math
from datetime import datetime, timezone
from mayinela.core.client import client
from mayinela.core.config import settings
from mayinela.core.registry import command, COMMANDS
from mayinela.core.utils import START_TIME, fmt_uptime, entity_name
from mayinela.core.database import db

@command("ping", "Comprueba la respuesta del userbot.", "Sistema")
async def ping(e, a):
    t = time.perf_counter()
    await e.edit("🏓 Pong…")
    await e.edit(f"🏓 Pong: {(time.perf_counter()-t)*1000:.0f} ms")

@command("alive", "Muestra el estado de Mayinela.", "Sistema")
async def alive(e, a):
    await e.edit(f"🌸 Mayinela activa\n⏱️ {fmt_uptime(time.time()-START_TIME)}")

@command("uptime", "Tiempo desde el arranque.", "Sistema")
async def uptime(e, a):
    await e.edit(f"⏱️ {fmt_uptime(time.time()-START_TIME)}")

@command("id", "Muestra IDs del mensaje y chat.", "Telegram")
async def idcmd(e, a):
    await e.edit(f"🆔 Chat: `{e.chat_id}`\nMensaje: `{e.id}`\nRemitente: `{e.sender_id}`")

@command("info", "Información del chat actual.", "Telegram")
async def info(e, a):
    chat = await e.get_chat()
    await e.edit(f"ℹ️ {entity_name(chat)}\nID: `{e.chat_id}`\nTipo: `{type(chat).__name__}`")

@command("me", "Información de tu cuenta.", "Telegram")
async def me(e, a):
    me = await client.get_me()
    await e.edit(f"👤 {entity_name(me)}\nID: `{me.id}`\nUsername: @{me.username or 'sin username'}")

@command("sysinfo", "Información básica de Termux/Android.", "Sistema")
async def sysinfo(e, a):
    mem = "desconocida"
    try:
        total = avail = None
        with open('/proc/meminfo', encoding='utf-8') as f:
            for line in f:
                k, v = line.split(':', 1)
                n = int(v.strip().split()[0])
                if k == 'MemTotal': total = n
                elif k == 'MemAvailable': avail = n
        if total and avail:
            mem = f"{(1-avail/total)*100:.1f}% usada"
    except Exception:
        pass
    await e.edit(f"📱 {platform.system()} {platform.release()}\n🐍 Python {platform.python_version()}\n💾 RAM: {mem}")

@command("stats", "Estadísticas de comandos.", "Sistema")
async def stats(e, a):
    rows = await db.get_stats()
    await e.edit("📊 Sin estadísticas aún." if not rows else "📊 Comandos más usados:\n" + "\n".join(f"`{c}` — {n}" for c,n in rows[:30]))




@command("setprefix", "Indica cómo cambiar el prefijo sin tocar la variable PREFIX de Termux.", "Configuración", owner=True)
async def setprefix(e, a):
    await e.edit("ℹ️ Edita `MAYINELA_PREFIX=` en .env y reinicia Mayinela.")

@command("restart", "Detiene la sesión para reiniciarla desde Termux.", "Sistema", owner=True)
async def restart(e, a):
    await e.edit("♻️ Cierra este proceso con CTRL+C y ejecuta `python main.py` de nuevo.")
