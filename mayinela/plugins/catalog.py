"""Mayinela: comandos útiles y reales, sin aliases ni comandos de relleno."""
import ast
import asyncio
import base64
import binascii
import hashlib
import json
import math
import os
import random
import re
import secrets
import string
import textwrap
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

from telethon import functions, types
from mayinela.core.client import client
from mayinela.core.config import settings
from mayinela.core.registry import command


def _reply(e):
    return e.get_reply_message()

async def _edit(e, text):
    # Telegram admite ~4096 caracteres; mantenemos margen para evitar MessageTooLongError.
    if len(text) <= 3900:
        await e.edit(text)
        return
    parts = [text[i:i+3800] for i in range(0, len(text), 3800)]
    await e.edit(parts[0])
    for p in parts[1:]:
        await client.send_message(e.chat_id, p)

async def _echo(e, a): await _edit(e, a or "Uso: escribe un texto.")
async def _upper(e, a): await _edit(e, a.upper() if a else "Uso: texto")
async def _lower(e, a): await _edit(e, a.lower() if a else "Uso: texto")
async def _title(e, a): await _edit(e, a.title() if a else "Uso: texto")
async def _swap(e, a): await _edit(e.swapcase() if a else "Uso: texto")
async def _reverse(e, a): await _edit(e, a[::-1] if a else "Uso: texto")
async def _length(e, a): await _edit(e, f"Caracteres: {len(a)}\nPalabras: {len(a.split())}\nLíneas: {len(a.splitlines())}")
async def _words(e, a): await _edit(e, f"Palabras: {len(a.split())}")
async def _lines(e, a): await _edit(e, f"Líneas: {len(a.splitlines())}")
async def _trim(e, a): await _edit(e, a.strip() if a else "Uso: texto")
async def _dedupe(e, a):
    lines=[]
    seen=set()
    for x in a.splitlines():
        if x not in seen: seen.add(x); lines.append(x)
    await _edit(e, "\n".join(lines) or "Sin líneas")
async def _sort(e, a): await _edit(e, "\n".join(sorted(a.splitlines(), key=str.casefold)) or "Uso: varias líneas")
async def _sortrev(e, a): await _edit(e, "\n".join(sorted(a.splitlines(), key=str.casefold, reverse=True)) or "Uso: varias líneas")
async def _count(e, a):
    if not a: return await _edit(e, "Uso: palabra | texto")
    p, _, t = a.partition("|")
    await _edit(e, f"{p.strip()}: {t.lower().count(p.strip().lower())}")
async def _repeat(e, a):
    m=re.match(r"(\d+)\s+([\s\S]+)",a)
    if not m: return await _edit(e,"Uso: número texto")
    n=min(int(m.group(1)),50); await _edit(e, (m.group(2)+"\n")*n)
async def _wrap(e, a):
    m=re.match(r"(\d+)\s+([\s\S]+)",a)
    if not m: return await _edit(e,"Uso: ancho texto")
    await _edit(e,"\n".join(textwrap.wrap(m.group(2), width=max(1,min(200,int(m.group(1)))))))
async def _replace(e,a):
    old,sep,rest=a.partition("|"); new,sep2,text=rest.partition("|")
    if not sep or not sep2: return await _edit(e,"Uso: viejo | nuevo | texto")
    await _edit(e,text.replace(old,new))
async def _slug(e,a):
    s=re.sub(r"[^\w\s-]","",a,flags=re.UNICODE).strip().lower(); await _edit(e,re.sub(r"[-\s]+","-",s))
async def _ascii(e,a): await _edit(e,a.encode("ascii","ignore").decode() if a else "Uso: texto")
async def _codepoints(e,a): await _edit(e," ".join(f"U+{ord(c):04X}" for c in a) if a else "Uso: texto")
async def _charat(e,a):
    try: await _edit(e, a.split(" ",1)[0] + ": " + a.split(" ",1)[1][int(a.split(" ",1)[0])])
    except Exception: await _edit(e,"Uso: índice texto")

async def _b64e(e,a): await _edit(e,base64.b64encode(a.encode()).decode() if a else "Uso: texto")
async def _b64d(e,a):
    try: await _edit(e,base64.b64decode(a).decode(errors="replace"))
    except Exception as x: await _edit(e,f"❌ Base64: {x}")
async def _hex(e,a): await _edit(e,a.encode().hex() if a else "Uso: texto")
async def _unhex(e,a):
    try: await _edit(e,bytes.fromhex(a).decode(errors="replace"))
    except Exception as x: await _edit(e,f"❌ Hex: {x}")
async def _urlenc(e,a): await _edit(e,quote(a,safe=""))
async def _urldec(e,a): await _edit(e,unquote(a))
async def _jsonpretty(e,a):
    try: await _edit(e,json.dumps(json.loads(a),ensure_ascii=False,indent=2))
    except Exception as x: await _edit(e,f"❌ JSON: {x}")
async def _jsonmin(e,a):
    try: await _edit(e,json.dumps(json.loads(a),ensure_ascii=False,separators=(",",":")))
    except Exception as x: await _edit(e,f"❌ JSON: {x}")
async def _hash(e,a,alg):
    if not a: return await _edit(e,"Uso: texto")
    await _edit(e,getattr(hashlib,alg)(a.encode()).hexdigest())
async def _sha1(e,a): await _hash(e,a,"sha1")
async def _sha256(e,a): await _hash(e,a,"sha256")
async def _sha512(e,a): await _hash(e,a,"sha512")
async def _md5(e,a): await _hash(e,a,"md5")
async def _randomhex(e,a): await _edit(e,secrets.token_hex(min(max(int(a or 16),1),64)))
async def _uuid(e,a): await _edit(e,str(uuid.uuid4()))

class SafeEval(ast.NodeVisitor):
    allowed=(ast.Expression,ast.Constant,ast.UnaryOp,ast.BinOp,ast.Add,ast.Sub,ast.Mult,ast.Div,ast.FloorDiv,ast.Mod,ast.Pow,ast.USub,ast.UAdd,ast.Call,ast.Name,ast.Load)
    names={k:getattr(math,k) for k in ("sqrt","sin","cos","tan","log","log10","fabs","ceil","floor")}
    def visit(self,node):
        if not isinstance(node,self.allowed): raise ValueError("expresión no permitida")
        return super().visit(node)
    def visit_Expression(self,node): return self.visit(node.body)
    def visit_Constant(self,node):
        if isinstance(node.value,(int,float)) and abs(node.value)<10**100: return node.value
        raise ValueError("constante no permitida")
    def visit_UnaryOp(self,node): return self._op(node.op)(self.visit(node.operand))
    def visit_BinOp(self,node):
        a,b=self.visit(node.left),self.visit(node.right); return self._op(node.op)(a,b)
    def visit_Call(self,node):
        if not isinstance(node.func,ast.Name) or node.func.id not in self.names: raise ValueError("función no permitida")
        return self.names[node.func.id](*[self.visit(x) for x in node.args])
    def visit_Name(self,node): raise ValueError("nombre no permitido")
    @staticmethod
    def _op(op):
        return {ast.Add:lambda a,b:a+b,ast.Sub:lambda a,b:a-b,ast.Mult:lambda a,b:a*b,ast.Div:lambda a,b:a/b,ast.FloorDiv:lambda a,b:a//b,ast.Mod:lambda a,b:a%b,ast.Pow:lambda a,b:a**b,ast.USub:lambda a:-a,ast.UAdd:lambda a:+a}[type(op)]
async def _calc(e,a):
    try: await _edit(e,str(SafeEval().visit(ast.parse(a,mode="eval"))))
    except Exception as x: await _edit(e,f"❌ Cálculo: {x}")
async def _percent(e,a):
    try:
        x,y=map(float,a.replace(",",".").split()); await _edit(e,f"{x}% de {y} = {x*y/100:g}")
    except: await _edit(e,"Uso: porcentaje cantidad")
async def _sqrt(e,a):
    try: await _edit(e,str(math.sqrt(float(a))))
    except: await _edit(e,"Uso: número")
async def _round(e,a):
    try: await _edit(e,str(round(float(a))))
    except: await _edit(e,"Uso: número")

async def _time(e,a): await _edit(e,datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"))
async def _utc(e,a): await _edit(e,datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
async def _unix(e,a): await _edit(e,str(int(time.time())))
async def _timestamp(e,a):
    try: await _edit(e,datetime.fromtimestamp(float(a)).astimezone().isoformat())
    except: await _edit(e,"Uso: timestamp Unix")
async def _date(e,a): await _edit(e,datetime.now().astimezone().strftime("%d/%m/%Y"))
async def _iso(e,a): await _edit(e,datetime.now().astimezone().isoformat())
async def _sleep(e,a):
    try: n=min(max(float(a),0),30); await e.edit(f"⏳ {n:g}s"); await asyncio.sleep(n); await e.edit("⏰ Listo")
    except: await _edit(e,"Uso: segundos")
async def _dice(e,a):
    m=re.match(r"(\d+)?d(\d+)",a.lower() or "1d6")
    if not m: return await _edit(e,"Uso: 2d6")
    n=min(int(m.group(1) or 1),100); sides=min(int(m.group(2)),10000); r=[random.randint(1,sides) for _ in range(n)]; await _edit(e,f"🎲 {r}\nTotal: {sum(r)}")
async def _coin(e,a): await _edit(e,random.choice(["🪙 Cara","🪙 Cruz"]))
async def _choose(e,a):
    xs=[x.strip() for x in a.split("|") if x.strip()]; await _edit(e,random.choice(xs) if xs else "Uso: opción | opción")
async def _randint(e,a):
    try:
        x,y=map(int,a.split()); await _edit(e,str(random.randint(x,y)))
    except: await _edit(e,"Uso: mínimo máximo")
async def _password(e,a):
    n=min(max(int(a or 16),4),128); chars=string.ascii_letters+string.digits+"!@#$%^&*_-"; await _edit(e,"".join(secrets.choice(chars) for _ in range(n)))

async def _id(e,a): await _edit(e,f"🆔 Chat `{e.chat_id}`\nMensaje `{e.id}`\nUsuario `{e.sender_id}`")
async def _chat(e,a):
    c=await e.get_chat(); await _edit(e,f"💬 {getattr(c,'title',None) or getattr(c,'first_name',None) or 'Chat'}\nID: `{e.chat_id}`\nTipo: `{type(c).__name__}`")
async def _me(e,a):
    m=await client.get_me(); await _edit(e,f"👤 {m.first_name or ''} {m.last_name or ''}\nID: `{m.id}`\n@{m.username or 'sin_username'}")
async def _replyinfo(e,a):
    r=await _reply(e)
    if not r: return await _edit(e,"Responde a un mensaje.")
    await _edit(e,f"↩️ ID `{r.id}`\n👤 `{r.sender_id}`\n💬 {r.raw_text[:1000] if r.raw_text else '[sin texto]'}")
async def _delete(e,a):
    ids=[]
    r=await _reply(e)
    if r: ids.append(r.id)
    ids.append(e.id)
    await client.delete_messages(e.chat_id,ids)
async def _pin(e,a):
    r=await _reply(e)
    if not r: return await _edit(e,"Responde a un mensaje para fijarlo.")
    await client(functions.messages.UpdatePinnedMessageRequest(peer=e.chat_id,id=r.id,silent=True,unpin=False,pm_oneside=False))
    await _edit(e,"📌 Mensaje fijado.")
async def _unpin(e,a):
    r=await _reply(e)
    if not r: return await _edit(e,"Responde al mensaje.")
    await client(functions.messages.UpdatePinnedMessageRequest(peer=e.chat_id,id=r.id,silent=True,unpin=True,pm_oneside=False)); await _edit(e,"📌 Desfijado.")
async def _purge(e,a):
    n=min(max(int(a or 10),1),100); msgs=[m async for m in client.iter_messages(e.chat_id,limit=n+1)]; await client.delete_messages(e.chat_id,[m.id for m in msgs])
async def _history(e,a):
    n=min(max(int(a or 10),1),50); msgs=[m async for m in client.iter_messages(e.chat_id,limit=n)]; await _edit(e,"\n".join(f"`{m.id}` {m.raw_text[:100]}" for m in reversed(msgs)))
async def _admins(e,a):
    admins=[]
    async for u in client.iter_participants(e.chat_id,filter=types.ChannelParticipantsAdmins): admins.append(f"• {u.id} — {u.first_name or ''} {u.last_name or ''}")
    await _edit(e,"👮 Administradores:\n"+"\n".join(admins[:100]) if admins else "No pude obtener administradores.")
async def _members(e,a):
    c=await e.get_chat(); count=getattr(c,'participants_count',None); await _edit(e,f"👥 Miembros: {count if count is not None else 'no disponible'}")
async def _mute(e,a):
    r=await _reply(e)
    if not r: return await _edit(e,"Responde al usuario que quieres silenciar.")
    await client(functions.channels.EditBannedRequest(e.chat_id,r.sender_id,types.ChatBannedRights(until_date=None,send_messages=True))); await _edit(e,"🔇 Usuario silenciado.")
async def _unmute(e,a):
    r=await _reply(e)
    if not r: return await _edit(e,"Responde al usuario.")
    await client(functions.channels.EditBannedRequest(e.chat_id,r.sender_id,types.ChatBannedRights(until_date=None,send_messages=False))); await _edit(e,"🔊 Usuario habilitado.")
async def _ban(e,a):
    r=await _reply(e)
    if not r: return await _edit(e,"Responde al usuario.")
    await client(functions.channels.EditBannedRequest(e.chat_id,r.sender_id,types.ChatBannedRights(until_date=None,view_messages=True))); await _edit(e,"🚫 Usuario expulsado/bloqueado.")
async def _unban(e,a):
    r=await _reply(e)
    if not r: return await _edit(e,"Responde al usuario.")
    await client(functions.channels.EditBannedRequest(e.chat_id,r.sender_id,types.ChatBannedRights(until_date=None))); await _edit(e,"✅ Usuario desbloqueado en el chat.")
async def _promote(e,a):
    r=await _reply(e)
    if not r: return await _edit(e,"Responde al usuario.")
    await client(functions.channels.EditAdminRequest(e.chat_id,r.sender_id,admin_rights=types.ChatAdminRights(change_info=True,post_messages=True,edit_messages=True,delete_messages=True,ban_users=True,invite_users=True,pin_messages=True,manage_call=True,other=True),rank="Mayinela")); await _edit(e,"⬆️ Usuario promovido.")
async def _demote(e,a):
    r=await _reply(e)
    if not r: return await _edit(e,"Responde al usuario.")
    await client(functions.channels.EditAdminRequest(e.chat_id,r.sender_id,admin_rights=types.ChatAdminRights(),rank="")); await _edit(e,"⬇️ Usuario degradado.")
async def _tag(e,a):
    r=await _reply(e)
    if not r: return await _edit(e,"Responde a un usuario.")
    u=await r.get_sender(); name=getattr(u,'first_name',None) or 'usuario'; await _edit(e,f"[{name}](tg://user?id={u.id})")

async def _files(e,a):
    p=Path(a or ".");
    if not p.exists(): return await _edit(e,"Ruta no encontrada.")
    items=list(p.iterdir())[:100]; await _edit(e,"\n".join(("📁 " if x.is_dir() else "📄 ")+x.name for x in items) or "Vacío")
async def _pwd(e,a): await _edit(e,os.getcwd())
async def _env(e,a):
    # Nunca revela API_HASH, API_ID, PHONE ni tokens.
    safe={"MAYINELA_PREFIX":settings.prefix,"SESSION_NAME":settings.session_name,"DB_PATH":settings.db_path,"LOG_LEVEL":settings.log_level}
    await _edit(e,"\n".join(f"{k}={v}" for k,v in safe.items()))
async def _fileinfo(e,a):
    p=Path(a)
    try: s=p.stat(); await _edit(e,f"📄 {p}\nTamaño: {s.st_size} bytes\nModificado: {datetime.fromtimestamp(s.st_mtime).isoformat()}")
    except Exception as x: await _edit(e,f"❌ {x}")
async def _write(e,a):
    name,sep,text=a.partition("|")
    if not sep: return await _edit(e,"Uso: archivo | contenido")
    p=Path(name).name; Path(p).write_text(text,encoding="utf-8"); await _edit(e,f"💾 Guardado: {p}")
async def _read(e,a):
    try: await _edit(e,Path(a).read_text(encoding="utf-8")[:3800])
    except Exception as x: await _edit(e,f"❌ {x}")
async def _mkdir(e,a):
    try: Path(a).mkdir(parents=True,exist_ok=True); await _edit(e,f"📁 Creado: {a}")
    except Exception as x: await _edit(e,f"❌ {x}")
async def _qr(e,a):
    if not a: return await _edit(e,"Uso: texto o URL")
    try:
        import qrcode
        p=Path("data/mayinela_qr.png"); p.parent.mkdir(exist_ok=True); qrcode.make(a).save(p); await client.send_file(e.chat_id,str(p),caption="🔳 QR generado"); await e.delete()
    except Exception as x: await _edit(e,f"❌ QR: {x}")

async def _send(e,a):
    if not a: return await _edit(e,"Uso: texto")
    await client.send_message(e.chat_id,a); await e.delete()
async def _meow(e,a): await _edit(e,"🐱 miau")
async def _shrug(e,a): await _edit(e,"¯\\_(ツ)_/¯")
async def _tableflip(e,a): await _edit(e,"(╯°□°）╯︵ ┻━┻")
async def _unflip(e,a): await _edit(e,"┬─┬ ノ( ゜-゜ノ)")
async def _8ball(e,a): await _edit(e,random.choice(["🎱 Sí","🎱 No","🎱 Probablemente","🎱 No lo sé","🎱 Pregunta de nuevo"]))
async def _choosecolor(e,a): await _edit(e,"#"+secrets.token_hex(3))
async def _quote(e,a): await _edit(e,("“"+a+"”") if a else "Uso: texto")
async def _listcats(e,a):
    # Dispatcher registra la metadata en tiempo de carga; esta función se completa en main.
    from mayinela.core.registry import COMMANDS
    cats=sorted({m._mayinela['category'] for m in COMMANDS.values()}); await _edit(e,"\n".join("• "+x for x in cats))

# Registro de funciones base y alias reales.
BASE = {
    "echo":("Texto","Repite el texto.",_echo), "upper":("Texto","Convierte a mayúsculas.",_upper), "lower":("Texto","Convierte a minúsculas.",_lower),
    "title":("Texto","Capitaliza palabras.",_title), "swapcase":("Texto","Invierte mayúsculas/minúsculas.",_swap), "reverse":("Texto","Invierte el texto.",_reverse),
    "length":("Texto","Cuenta caracteres.",_length), "words":("Texto","Cuenta palabras.",_words), "lines":("Texto","Cuenta líneas.",_lines),
    "trim":("Texto","Quita espacios exteriores.",_trim), "dedupe":("Texto","Elimina líneas duplicadas.",_dedupe), "sort":("Texto","Ordena líneas.",_sort), "sortrev":("Texto","Ordena líneas al revés.",_sortrev),
    "count":("Texto","Cuenta una palabra usando 'palabra | texto'.",_count), "repeat":("Texto","Repite texto N veces.",_repeat), "wrap":("Texto","Envuelve texto a un ancho.",_wrap), "replace":("Texto","Reemplaza texto con separadores |.",_replace),
    "slug":("Texto","Crea un slug.",_slug), "ascii":("Texto","Quita caracteres no ASCII.",_ascii), "codepoints":("Texto","Muestra puntos Unicode.",_codepoints), "charat":("Texto","Obtiene un carácter por índice.",_charat),
    "b64e":("Codificación","Codifica Base64.",_b64e), "b64d":("Codificación","Decodifica Base64.",_b64d), "hex":("Codificación","Codifica hexadecimal.",_hex), "unhex":("Codificación","Decodifica hexadecimal.",_unhex),
    "urlenc":("Codificación","Codifica una URL.",_urlenc), "urldec":("Codificación","Decodifica una URL.",_urldec), "jsonpretty":("Codificación","Formatea JSON.",_jsonpretty), "jsonmin":("Codificación","Minifica JSON.",_jsonmin),
    "sha1":("Seguridad","Hash SHA-1.",_sha1), "sha256":("Seguridad","Hash SHA-256.",_sha256), "sha512":("Seguridad","Hash SHA-512.",_sha512), "md5":("Seguridad","Hash MD5.",_md5), "randomhex":("Seguridad","Hex aleatorio.",_randomhex), "uuid":("Seguridad","UUID aleatorio.",_uuid),
    "calc":("Matemática","Calculadora segura.",_calc), "percent":("Matemática","Calcula porcentaje.",_percent), "sqrt":("Matemática","Raíz cuadrada.",_sqrt), "round":("Matemática","Redondea un número.",_round),
    "time":("Tiempo","Hora local.",_time), "utc":("Tiempo","Hora UTC.",_utc), "unix":("Tiempo","Timestamp Unix.",_unix), "timestamp":("Tiempo","Convierte timestamp a fecha.",_timestamp), "date":("Tiempo","Fecha local.",_date), "iso":("Tiempo","Fecha ISO.",_iso), "sleep":("Tiempo","Espera N segundos.",_sleep),
    "dice":("Aleatorio","Tira dados, por ejemplo 2d6.",_dice), "coin":("Aleatorio","Lanza una moneda.",_coin), "choose":("Aleatorio","Elige entre opciones separadas por |.",_choose), "randint":("Aleatorio","Número aleatorio entre límites.",_randint), "password":("Aleatorio","Genera una contraseña aleatoria.",_password), "color":("Aleatorio","Genera un color hexadecimal.",_choosecolor),
    "id":("Telegram","Muestra IDs.",_id), "chat":("Telegram","Información del chat.",_chat), "me":("Telegram","Información de tu cuenta.",_me), "replyinfo":("Telegram","Información del mensaje respondido.",_replyinfo), "delete":("Telegram","Elimina el mensaje respondido y el comando.",_delete), "pin":("Telegram","Fija el mensaje respondido.",_pin), "unpin":("Telegram","Desfija el mensaje respondido.",_unpin), "purge":("Telegram","Borra los últimos N mensajes.",_purge), "history":("Telegram","Muestra IDs de mensajes recientes.",_history), "admins":("Telegram","Lista administradores.",_admins), "members":("Telegram","Muestra el contador de miembros.",_members), "mute":("Moderación","Silencia al usuario respondido.",_mute), "unmute":("Moderación","Quita el silencio.",_unmute), "ban":("Moderación","Bloquea al usuario respondido.",_ban), "unban":("Moderación","Desbloquea al usuario respondido.",_unban), "promote":("Moderación","Promueve al usuario respondido.",_promote), "demote":("Moderación","Quita administración.",_demote), "tag":("Telegram","Menciona al usuario respondido.",_tag),
    "files":("Archivos","Lista archivos de una ruta.",_files), "pwd":("Archivos","Muestra el directorio actual.",_pwd), "env":("Sistema","Muestra configuración segura.",_env), "fileinfo":("Archivos","Información de un archivo.",_fileinfo), "write":("Archivos","Escribe archivo: nombre | contenido.",_write), "read":("Archivos","Lee un archivo de texto.",_read), "mkdir":("Archivos","Crea una carpeta.",_mkdir), "qr":("Multimedia","Genera y envía un QR.",_qr), "send":("Telegram","Envía un texto sin conservar el comando.",_send),
    "meow":("Diversión","Miau.",_meow), "shrug":("Diversión","Emoticono shrug.",_shrug), "tableflip":("Diversión","Table flip.",_tableflip), "unflip":("Diversión","Recoloca la mesa.",_unflip), "8ball":("Diversión","Bola 8.",_8ball), "quote":("Texto","Añade comillas tipográficas.",_quote), "categories":("Ayuda","Lista categorías.",_listcats),
}

for name,(cat,desc,func) in BASE.items():
    command(name, desc, cat)(func)

