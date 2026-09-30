"""Moderación, GBAN, filtros y anti-spam para Mayinela V5."""
import asyncio
import json
import time
from collections import defaultdict, deque
from pathlib import Path

from telethon import events, functions, types

from mayinela.core.client import client
from mayinela.core.config import settings
from mayinela.core.registry import command

DATA = Path("data")
GBAN_FILE = DATA / "gban.json"
FILTER_FILE = DATA / "filters.json"
WARN_FILE = DATA / "warnings.json"
ANTI_FILE = DATA / "antispam.json"

DEFAULT_THRESHOLD = 6
DEFAULT_WINDOW = 10
DEFAULT_MUTE = 10 * 60

SPAM_BUCKETS = defaultdict(deque)
SPAM_LOCK = asyncio.Lock()


def _load(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def _save(path, data):
    DATA.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _gban():
    return {str(x) for x in _load(GBAN_FILE, [])}


def _filters():
    return _load(FILTER_FILE, {})


def _warnings():
    return _load(WARN_FILE, {})


def _antispam():
    return _load(ANTI_FILE, {})


async def _reply_user(event):
    reply = await event.get_reply_message()
    if not reply or not reply.sender_id:
        await event.edit("↩️ Responde al mensaje del usuario.")
        return None
    return reply.sender_id


async def _is_group(event):
    return bool(event.is_group or event.is_channel)


async def _apply_ban(chat_id, user_id, delete=True):
    rights = types.ChatBannedRights(until_date=None, view_messages=True)
    await client(functions.channels.EditBannedRequest(channel=chat_id, participant=user_id, banned_rights=rights))
    if delete:
        try:
            await client.delete_messages(chat_id, [user_id])
        except Exception:
            pass


async def _mute(chat_id, user_id, seconds):
    until = int(time.time() + seconds)
    rights = types.ChatBannedRights(until_date=until, send_messages=True)
    await client(functions.channels.EditBannedRequest(channel=chat_id, participant=user_id, banned_rights=rights))


async def _unmute(chat_id, user_id):
    rights = types.ChatBannedRights(until_date=None, send_messages=False)
    await client(functions.channels.EditBannedRequest(channel=chat_id, participant=user_id, banned_rights=rights))


@command("kick", "Expulsa al usuario respondido del grupo.", "Moderación", owner=True)
async def kick(e, a):
    if not await _is_group(e):
        return await e.edit("⚠️ Este comando solo funciona en grupos.")
    uid = await _reply_user(e)
    if uid is None:
        return
    rights = types.ChatBannedRights(until_date=None, view_messages=True)
    await client(functions.channels.EditBannedRequest(channel=e.chat_id, participant=uid, banned_rights=rights))
    # Unban inmediato = expulsar, permitiendo volver a entrar si tiene invitación.
    await client(functions.channels.EditBannedRequest(channel=e.chat_id, participant=uid, banned_rights=types.ChatBannedRights()))
    await e.edit("👢 Usuario expulsado.")


@command("warn", "Añade una advertencia; al llegar a 3, silencia 10 minutos.", "Moderación", owner=True)
async def warn(e, a):
    if not await _is_group(e):
        return await e.edit("⚠️ Solo funciona en grupos.")
    uid = await _reply_user(e)
    if uid is None:
        return
    data = _warnings()
    key = str(e.chat_id)
    data.setdefault(key, {})
    ukey = str(uid)
    data[key][ukey] = int(data[key].get(ukey, 0)) + 1
    count = data[key][ukey]
    if count >= 3:
        await _mute(e.chat_id, uid, DEFAULT_MUTE)
        data[key][ukey] = 0
        _save(WARN_FILE, data)
        return await e.edit("⚠️ 3 advertencias → 🔇 usuario silenciado durante 10 minutos.")
    _save(WARN_FILE, data)
    await e.edit(f"⚠️ Advertencia {count}/3 para `{uid}`.")


@command("unwarn", "Quita una advertencia al usuario respondido.", "Moderación", owner=True)
async def unwarn(e, a):
    if not await _is_group(e):
        return await e.edit("⚠️ Solo funciona en grupos.")
    uid = await _reply_user(e)
    if uid is None:
        return
    data = _warnings()
    key, ukey = str(e.chat_id), str(uid)
    count = max(0, int(data.get(key, {}).get(ukey, 0)) - 1)
    data.setdefault(key, {})[ukey] = count
    _save(WARN_FILE, data)
    await e.edit(f"✅ Advertencias restantes: {count}.")


@command("warnings", "Muestra las advertencias del usuario respondido.", "Moderación", owner=True)
async def warnings(e, a):
    if not await _is_group(e):
        return await e.edit("⚠️ Solo funciona en grupos.")
    uid = await _reply_user(e)
    if uid is None:
        return
    data = _warnings()
    count = int(data.get(str(e.chat_id), {}).get(str(uid), 0))
    await e.edit(f"⚠️ Usuario `{uid}` tiene **{count}/3** advertencias.")


@command("filter", "Añade una palabra/frase que se eliminará automáticamente.", "Filtros", owner=True)
async def add_filter(e, a):
    word = a.strip().casefold()
    if not word:
        return await e.edit(f"Uso: {settings.prefix}filter palabra o frase")
    if not await _is_group(e):
        return await e.edit("⚠️ Solo funciona en grupos.")
    data = _filters()
    key = str(e.chat_id)
    items = set(data.get(key, []))
    items.add(word)
    data[key] = sorted(items)
    _save(FILTER_FILE, data)
    await e.edit(f"🧹 Filtro añadido: `{word}`")


@command("unfilter", "Elimina un filtro del grupo.", "Filtros", owner=True)
async def remove_filter(e, a):
    word = a.strip().casefold()
    if not word:
        return await e.edit(f"Uso: {settings.prefix}unfilter palabra")
    data = _filters()
    key = str(e.chat_id)
    items = set(data.get(key, []))
    items.discard(word)
    data[key] = sorted(items)
    _save(FILTER_FILE, data)
    await e.edit(f"✅ Filtro eliminado: `{word}`")


@command("filters", "Muestra los filtros activos del grupo.", "Filtros", owner=True)
async def list_filters(e, a):
    items = _filters().get(str(e.chat_id), [])
    await e.edit("🧹 No hay filtros activos." if not items else "🧹 Filtros:\n" + "\n".join(f"• `{x}`" for x in items))


@command("gban", "Banea globalmente al usuario respondido en los grupos protegidos.", "GBAN", owner=True)
async def gban(e, a):
    uid = await _reply_user(e)
    if uid is None:
        return
    bans = _gban()
    bans.add(str(uid))
    _save(GBAN_FILE, sorted(bans, key=int))
    if await _is_group(e):
        try:
            await client(functions.channels.EditBannedRequest(
                channel=e.chat_id,
                participant=uid,
                banned_rights=types.ChatBannedRights(until_date=None, view_messages=True),
            ))
        except Exception:
            pass
    await e.edit(f"🌐🚫 GBAN activo para `{uid}`.")


@command("ungban", "Quita al usuario de la lista GBAN.", "GBAN", owner=True)
async def ungban(e, a):
    uid = await _reply_user(e)
    if uid is None and a.isdigit():
        uid = int(a)
    if uid is None:
        return await e.edit(f"Uso: responde al usuario o {settings.prefix}ungban ID")
    bans = _gban()
    bans.discard(str(uid))
    _save(GBAN_FILE, sorted(bans, key=int))
    await e.edit(f"✅ `{uid}` eliminado del GBAN.")


@command("gbanlist", "Lista los IDs incluidos en GBAN.", "GBAN", owner=True)
async def gbanlist(e, a):
    bans = sorted(_gban(), key=int)
    await e.edit("🌐 GBAN vacío." if not bans else "🌐 GBAN:\n" + "\n".join(f"• `{x}`" for x in bans[:200]))


@command("gbancheck", "Comprueba si un ID está en GBAN.", "GBAN", owner=True)
async def gbancheck(e, a):
    uid = a.strip()
    if not uid.isdigit():
        uid = str((await e.get_sender()).id)
    await e.edit("🚫 Está en GBAN." if uid in _gban() else "✅ No está en GBAN.")


@command("antispam", "Activa/desactiva el anti-spam en este grupo.", "Anti-spam", owner=True)
async def antispam(e, a):
    if not await _is_group(e):
        return await e.edit("⚠️ Solo funciona en grupos.")
    value = a.strip().lower()
    data = _antispam()
    key = str(e.chat_id)
    if value in {"on", "1", "si", "sí", "activar"}:
        data[key] = True
        _save(ANTI_FILE, data)
        return await e.edit("🛡️ Anti-spam activado: 6 mensajes en 10 segundos → silencio 10 minutos.")
    if value in {"off", "0", "no", "desactivar"}:
        data.pop(key, None)
        _save(ANTI_FILE, data)
        return await e.edit("🛡️ Anti-spam desactivado.")
    await e.edit(f"Uso: {settings.prefix}antispam on|off")


@command("antispamstatus", "Muestra el estado del anti-spam.", "Anti-spam", owner=True)
async def antispamstatus(e, a):
    active = bool(_antispam().get(str(e.chat_id), False))
    await e.edit(f"🛡️ Anti-spam: {'ACTIVO' if active else 'INACTIVO'}\n📈 Umbral: {DEFAULT_THRESHOLD} mensajes / {DEFAULT_WINDOW}s\n🔇 Acción: silencio {DEFAULT_MUTE//60} min")


async def _sender_is_admin(chat_id, uid):
    if uid == settings.owner_id:
        return True
    try:
        p = await client.get_permissions(chat_id, uid)
        return bool(getattr(p, "is_admin", False) or getattr(p, "is_creator", False))
    except Exception:
        return False


@client.on(events.NewMessage(incoming=True))
async def moderation_guard(event):
    if not (event.is_group or event.is_channel) or not event.sender_id:
        return
    uid = event.sender_id
    if uid == settings.owner_id or await _sender_is_admin(event.chat_id, uid):
        return

    # GBAN tiene prioridad.
    if str(uid) in _gban():
        try:
            await client(functions.channels.EditBannedRequest(
                channel=event.chat_id,
                participant=uid,
                banned_rights=types.ChatBannedRights(until_date=None, view_messages=True),
            ))
        except Exception:
            pass
        return

    # Filtros de texto.
    text = (event.raw_text or "").casefold()
    if text:
        for word in _filters().get(str(event.chat_id), []):
            if word and word in text:
                try:
                    await event.delete()
                except Exception:
                    pass
                return

    # Anti-spam por velocidad de mensajes.
    if not _antispam().get(str(event.chat_id), False):
        return
    now = time.monotonic()
    key = (event.chat_id, uid)
    async with SPAM_LOCK:
        q = SPAM_BUCKETS[key]
        q.append(now)
        while q and now - q[0] > DEFAULT_WINDOW:
            q.popleft()
        hit = len(q) >= DEFAULT_THRESHOLD
        if hit:
            q.clear()
    if hit:
        try:
            await _mute(event.chat_id, uid, DEFAULT_MUTE)
            await event.respond(f"🛡️ Anti-spam: usuario `{uid}` silenciado 10 minutos.")
        except Exception:
            pass
