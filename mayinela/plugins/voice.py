"""V7 - voz TTS de Mayinela con estilo femenino/otaku."""
import asyncio
import os
import tempfile
from pathlib import Path

from telethon import events
from mayinela.core.client import client
from mayinela.core.config import settings
from mayinela.core.registry import command

try:
    import edge_tts
except ImportError:
    edge_tts = None

VOICE = os.getenv("MAYINELA_VOICE", "es-MX-DaliaNeural")
RATE = os.getenv("MAYINELA_VOICE_RATE", "+5%")
PITCH = os.getenv("MAYINELA_VOICE_PITCH", "+8Hz")
DATA_DIR = Path("data/voice")

VOICE_HELP = (
    "Convierte texto a voz con voz femenina en español y ajuste estilo otaku. "
    "Uso: .voz <texto> | .voz on/off | .voz status"
)


def _voice_available():
    return edge_tts is not None


async def _synthesize(text: str, output: Path):
    if not _voice_available():
        raise RuntimeError("Falta edge-tts. Instala las dependencias de requirements.txt.")
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(str(output))


@command("voz", VOICE_HELP, "Voz")
async def voz(e, a):
    arg = a.strip()
    if not arg:
        await e.edit(
            "🎙️ **Mayinela Voz**\n\n"
            f"• `{settings.prefix}voz <texto>` — habla el texto\n"
            f"• `{settings.prefix}voz on` — activa el modo voz\n"
            f"• `{settings.prefix}voz off` — desactiva el modo voz\n"
            f"• `{settings.prefix}voz status` — muestra el estado\n\n"
            f"🌸 Voz: `{VOICE}`\n"
            "🖤🩶🤍💜 Perfil: femenino · otaku"
        )
        return

    low = arg.lower()
    if low in {"on", "activar", "activa"}:
        await e.edit("🎙️🌸 Modo voz activado. Usa `.voz <texto>` para hablar.")
        return
    if low in {"off", "desactivar", "desactiva"}:
        await e.edit("🔇 Modo voz desactivado.")
        return
    if low in {"status", "estado"}:
        await e.edit(
            f"🎙️ Voz disponible: **{'sí' if _voice_available() else 'no'}**\n"
            f"🌸 Voz: `{VOICE}`\n"
            f"✨ Ajuste otaku: velocidad `{RATE}`, tono `{PITCH}`"
        )
        return

    text = arg[:1200]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="mayinela_", suffix=".mp3", dir=DATA_DIR)
    os.close(fd)
    output = Path(tmp)
    try:
        await e.edit("🎙️🌸 Preparando mi voz otaku…")
        await _synthesize(text, output)
        await client.send_file(e.chat_id, str(output), voice_note=True, caption="🌸🖤 Mayinela")
        await e.delete()
    except Exception as exc:
        await e.edit(f"❌ No pude generar la voz: `{type(exc).__name__}: {exc}`")
    finally:
        try:
            output.unlink(missing_ok=True)
        except Exception:
            pass
