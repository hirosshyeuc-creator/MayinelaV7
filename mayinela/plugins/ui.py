"""Mayinela V3: menú dinámico, estilo asexual y bucles de emojis."""
import asyncio
import json
import time
from pathlib import Path

from telethon import events, functions

from mayinela.core.client import client
from mayinela.core.config import settings
from mayinela.core.registry import command, COMMANDS

ACE = "🖤 🩶 🤍 💜"
STYLE = "🌸🖤🩶🤍💜🌸"
LOOP_MAX = 10 * 60
LOOP_INTERVAL = 2.5
LOOPS = {}
APPROVED_FILE = Path("data/approved_users.json")
PENDING_FILE = Path("data/pending_users.json")


def _load(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def _save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _approved():
    return set(str(x) for x in _load(APPROVED_FILE, []))


def _pending():
    return _load(PENDING_FILE, {})


def _categories():
    return sorted({m._mayinela["category"] for m in COMMANDS.values()})


def _menu_text():
    cats = {}
    for m in COMMANDS.values():
        cat = m._mayinela["category"]
        if cat == "Menú":
            continue
        cats[cat] = cats.get(cat, 0) + 1
    lines = [
        f"{STYLE}",
        "**MAYINELA · MENÚ**",
        "Menú único: aquí se consulta todo lo que puede hacer Mayinela.",
        f"🧰 **{len(COMMANDS)}** comandos registrados",
        f"📚 **{len(cats)}** categorías",
        "",
        f"⚙️ Prefijo actual: `{settings.prefix}`",
        "",
        "**Categorías**",
    ]
    for i, (cat, count) in enumerate(sorted(cats.items()), 1):
        lines.append(f"`{i:02}` · **{cat}** — {count}")
    lines += [
        "",
        "📖 Navegación:",
        f"• `{settings.prefix}menu` — este menú",
        f"• `{settings.prefix}menu <categoría>` — comandos de una categoría",
        f"• `{settings.prefix}menu all` — todos los comandos",
        f"• `{settings.prefix}menu all 2` — página 2",
        f"• `{settings.prefix}menu buscar <texto>` — buscar una herramienta",
        "",
        "🖤🩶🤍💜 Bandera asexual",
        "⏱️ Los bucles duran como máximo 10 minutos o hasta borrar su mensaje.",
    ]
    return "\n".join(lines)


def _category_text(cat):
    items = sorted(
        (m for m in COMMANDS.values() if m._mayinela["category"].lower() == cat.lower()),
        key=lambda x: x._mayinela["name"],
    )
    if not items:
        return None
    lines = [f"{STYLE}", f"**{cat}** · {len(items)} comandos", ""]
    for m in items:
        lines.append(f"`{settings.prefix}{m._mayinela['name']}` — {m._mayinela['help']}")
    lines += ["", f"↩️ `{settings.prefix}menu` para volver al menú principal."]
    return "\n".join(lines)


def _all_text(page=1, per_page=30):
    items = sorted(
        (m for m in COMMANDS.values() if m._mayinela["name"] != "menu"),
        key=lambda x: (x._mayinela["category"], x._mayinela["name"]),
    )
    pages = max(1, (len(items) + per_page - 1) // per_page)
    page = max(1, min(page, pages))
    chunk = items[(page - 1) * per_page: page * per_page]
    lines = [f"{STYLE}", f"**TODAS LAS HERRAMIENTAS** · página {page}/{pages}", ""]
    for m in chunk:
        lines.append(f"`{settings.prefix}{m._mayinela['name']}` — {m._mayinela['category']}")
    lines += ["", f"➡️ `{settings.prefix}menu all {page + 1}` para la siguiente página." if page < pages else "", f"↩️ `{settings.prefix}menu` para volver."]
    return "\n".join(x for x in lines if x != "")


def _search_text(term):
    term = term.lower().strip()
    if not term:
        return f"Uso: `{settings.prefix}menu buscar texto`"
    items = [m for m in COMMANDS.values() if term in m._mayinela["name"].lower() or term in m._mayinela["help"].lower() or term in m._mayinela["category"].lower()]
    items = sorted(items, key=lambda x: x._mayinela["name"])
    lines = [f"{STYLE}", f"**BÚSQUEDA:** `{term}` · {len(items)} resultados", ""]
    if not items:
        lines.append("No encontré herramientas con ese texto.")
    else:
        lines.extend(f"`{settings.prefix}{m._mayinela['name']}` — {m._mayinela['help']}" for m in items)
    lines += ["", f"↩️ `{settings.prefix}menu` para volver."]
    return "\n".join(lines)


@command("menu", "Menú único de Mayinela: categorías, búsqueda y todas las herramientas.", "Menú")
async def menu(e, a):
    arg = a.strip()
    if not arg:
        await e.edit(_menu_text())
        return
    parts = arg.split(None, 1)
    head = parts[0].lower()
    if head == "all":
        page = 1
        if len(parts) > 1 and parts[1].strip().isdigit():
            page = int(parts[1].strip())
        await e.edit(_all_text(page))
        return
    if head in {"buscar", "search"}:
        await e.edit(_search_text(parts[1] if len(parts) > 1 else ""))
        return
    if head.isdigit():
        cats = [c for c in _categories() if c != "Menú"]
        idx = int(head) - 1
        if 0 <= idx < len(cats):
            await e.edit(_category_text(cats[idx]))
            return
    text = _category_text(arg)
    if text:
        await e.edit(text)
        return
    await e.edit(_menu_text() + f"\n\n❌ Categoría no encontrada: `{arg}`")


async def _loop_message(chat_id, message_id, frames):
    key = (chat_id, message_id)
    started = time.monotonic()
    index = 0
    try:
        while time.monotonic() - started < LOOP_MAX:
            msg = await client.get_messages(chat_id, ids=message_id)
            if not msg:
                break
            await msg.edit(frames[index % len(frames)] + f"\n\n⏱️ {int(time.monotonic()-started)}s · {ACE}")
            index += 1
            await asyncio.sleep(LOOP_INTERVAL)
    except asyncio.CancelledError:
        pass
    except Exception:
        pass
    finally:
        LOOP_TASKS = globals().get("LOOPS", {})
        LOOP_TASKS.pop(key, None)


def _start_loop(e, frames):
    key = (e.chat_id, e.id)
    old = LOOPS.pop(key, None)
    if old:
        old.cancel()
    LOOPS[key] = asyncio.create_task(_loop_message(e.chat_id, e.id, frames))


def _loop_command(name, help_text, frames):
    @command(name, help_text, "Bucles")
    async def _cmd(e, a):
        _start_loop(e, frames)
        await e.edit(frames[0] + f"\n\n🔁 Bucle iniciado · máximo 10 min · borra este mensaje para detenerlo\n{ACE}")
    return _cmd


_LOOPSETS = {
    "loopace": ["🖤", "🩶", "🤍", "💜", "🖤🩶🤍💜"],
    "loopflag": [ACE, "🖤🩶🤍💜🖤", "🌸🖤🩶🤍💜🌸", "💜🤍🩶🖤"],
    "loopheart": ["🖤", "🩶", "🤍", "💜", "💜🤍🩶🖤"],
    "loopspark": ["✨", "🌟", "💫", "⭐", "🌸✨🌸"],
    "loopflower": ["🌸", "🌷", "🌺", "🪻", "🌸🪻🌸"],
    "loopstars": ["⭐", "🌟", "✨", "💫", "🌟✨⭐"],
    "loopmoon": ["🌙", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"],
    "looprainbow": ["❤️", "🧡", "💛", "💚", "💙", "💜"],
    "loopfem": ["🌸🖤", "🩶🤍", "💜🌸", "🖤🩶🤍💜"],
    "loopemoji": ["🌸", "🖤", "✨", "🩶", "🤍", "💜", "🌸✨"],
}

for _name, _frames in _LOOPSETS.items():
    _loop_command(_name, "Bucle de emojis; máximo 10 minutos o hasta borrar el mensaje.", _frames)


@command("stoploops", "Detiene todos los bucles activos de este chat.", "Bucles", owner=True)
async def stoploops(e, a):
    count = 0
    for key, task in list(LOOPS.items()):
        if key[0] == e.chat_id:
            task.cancel()
            LOOPS.pop(key, None)
            count += 1
    await e.edit(f"🛑 Detenidos {count} bucles. {ACE}")


@command("loopstatus", "Muestra cuántos bucles están activos.", "Bucles", owner=True)
async def loopstatus(e, a):
    n = sum(1 for chat_id, _ in LOOPS if chat_id == e.chat_id)
    await e.edit(f"🔁 Bucles activos en este chat: **{n}**\n{ACE}")


@client.on(events.NewMessage(incoming=True))
async def unknown_guard(event):
    if not event.is_private or event.sender_id is None or event.sender_id == settings.owner_id:
        return
    sender = await event.get_sender()
    if getattr(sender, "bot", False):
        return
    if getattr(sender, "contact", False):
        return
    uid = str(event.sender_id)
    approved = _approved()
    if uid in approved:
        return
    pending = _pending()
    entry = pending.get(uid, {"attempts": 0})
    entry["attempts"] = int(entry.get("attempts", 0)) + 1
    entry["last_message_id"] = event.id
    try:
        entry["name"] = getattr(sender, "first_name", None) or getattr(sender, "username", None) or uid
    except Exception:
        entry["name"] = uid
    if entry["attempts"] >= 3:
        try:
            await client(functions.contacts.BlockRequest(int(event.sender_id)))
            pending.pop(uid, None)
            _save(PENDING_FILE, pending)
            return
        except Exception:
            pass
    pending[uid] = entry
    _save(PENDING_FILE, pending)
    left = 3 - entry["attempts"]
    await event.reply(f"🌸 Este chat está protegido por Mayinela. Intentos restantes: **{left}**.\n{ACE}")


@command("pending", "Lista usuarios desconocidos pendientes de aprobación.", "Privacidad", owner=True)
async def pending(e, a):
    data = _pending()
    if not data:
        await e.edit("🛡️ No hay usuarios pendientes.")
        return
    lines = ["🛡️ **Pendientes**", ""]
    for uid, info in data.items():
        lines.append(f"• `{uid}` — {info.get('name','?')} — {info.get('attempts',0)}/3")
    lines.append(f"\nAprueba con `{settings.prefix}approve ID` o bloquea con `{settings.prefix}block ID`." )
    await e.edit("\n".join(lines))


@command("approve", "Aprueba un usuario pendiente: .approve ID", "Privacidad", owner=True)
async def approve(e, a):
    uid = a.strip().split()[0] if a.strip() else ""
    if not uid.isdigit():
        await e.edit(f"Uso: `{settings.prefix}approve ID`")
        return
    approved = _approved()
    approved.add(uid)
    _save(APPROVED_FILE, sorted(approved))
    pending = _pending()
    pending.pop(uid, None)
    _save(PENDING_FILE, pending)
    await e.edit(f"✅ Usuario `{uid}` aprobado. {ACE}")


@command("block", "Bloquea un usuario por ID: .block ID", "Privacidad", owner=True)
async def block(e, a):
    uid = a.strip().split()[0] if a.strip() else ""
    if not uid.isdigit():
        await e.edit(f"Uso: `{settings.prefix}block ID`")
        return
    try:
        await client(functions.contacts.BlockRequest(int(uid)))
        pending = _pending(); pending.pop(uid, None); _save(PENDING_FILE, pending)
        await e.edit(f"🚫 Usuario `{uid}` bloqueado.")
    except Exception as exc:
        await e.edit(f"❌ No pude bloquear `{uid}`: {type(exc).__name__}")
