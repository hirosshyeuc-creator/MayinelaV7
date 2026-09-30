# Mayinela V3

Userbot de Telegram para Termux con prefijo configurable (por defecto `.`).

## V3
- Menú dinámico con botones: `.menu`.
- Estética femenina/aseuxal con 🖤🩶🤍💜.
- Bucles de emojis: `.loopace`, `.loopflag`, `.loopheart`, `.loopspark`, `.loopflower`, `.loopstars`, `.loopmoon`, `.looprainbow`, `.loopfem`, `.loopemoji`.
- Cada bucle edita el mismo mensaje durante un máximo de 10 minutos y se detiene si borras ese mensaje.
- `.stoploops` detiene los bucles del chat.
- `.loopstatus` muestra los bucles activos.
- Protección de mensajes privados de desconocidos: 3 intentos; después se bloquea automáticamente si no fue aprobado.
- `.pending` lista pendientes; `.approve ID` aprueba; `.block ID` bloquea manualmente.
- Los usuarios marcados como contacto o previamente aprobados no pasan por la protección.

## Prefijo
En `.env` usa:

`MAYINELA_PREFIX=.`

No uses la variable `PREFIX` de Termux.


### V4
Se eliminaron los aliases y los comandos `toolXXX` de relleno. El menú ahora muestra únicamente comandos con una función concreta.

## V5 — Moderación, GBAN, filtros y anti-spam

### Moderación
- `.ban`, `.unban`, `.kick`
- `.mute`, `.unmute` (heredados del catálogo)
- `.warn`, `.unwarn`, `.warnings`
- `.promote`, `.demote`, `.purge`, `.pin`, `.unpin`

### GBAN
- `.gban` — responde al usuario para añadirlo al bloqueo global.
- `.ungban ID` o responde al usuario.
- `.gbanlist`
- `.gbancheck ID`

El guardián GBAN revisa mensajes entrantes en grupos donde Mayinela esté presente y tenga permisos para bloquear.

### Filtros
- `.filter palabra o frase`
- `.unfilter palabra o frase`
- `.filters`

Los mensajes que contengan un filtro activo se eliminan automáticamente.

### Anti-spam
- `.antispam on`
- `.antispam off`
- `.antispamstatus`

Por defecto detecta 6 mensajes del mismo usuario en 10 segundos y aplica un silencio de 10 minutos. Los administradores y la propietaria quedan excluidos.

Los comandos de esta sección están restringidos a la propietaria.

## V7 — Voz
- `.voz <texto>` genera una nota de voz.
- `.voz on/off` controla el modo voz informativo.
- `.voz status` comprueba TTS.
- Voz predeterminada: `es-MX-DaliaNeural`, con pequeños ajustes de velocidad y tono para un estilo femenino/otaku.
- Requiere conexión a Internet para generar el audio mediante Edge TTS.
