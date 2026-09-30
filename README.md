🌸 Mayinela V7

Mayinela V7 es un Userbot de Telegram desarrollado en Python para ejecutarse en Termux.

Incluye herramientas de Telegram, menú centralizado, moderación, filtros, anti-spam, comandos de utilidad y respuesta por voz.

---

📱 Instalación en Termux

1. Actualizar Termux

pkg update && pkg upgrade -y

2. Instalar Git, Python y herramientas necesarias

pkg install git python unzip -y

3. Descargar Mayinela

git clone https://github.com/hirosshyeuc-creator/MayinelaV7.git

4. Entrar en la carpeta

cd MayinelaV7

5. Instalar las dependencias

pip install -r requirements.txt

6. Crear el archivo de configuración

cp .env.example .env

7. Editar la configuración

nano .env

Introduce tus propias credenciales de Telegram en ".env".

Guarda el archivo y sal de "nano".

8. Iniciar Mayinela

python main.py

En el primer inicio, Telegram puede solicitar tu número y el código de inicio de sesión.

---

🌸 Comandos principales

El menú principal se abre con:

.menu

También puedes consultar las diferentes categorías y comandos desde el menú.

---

🔊 Voz

Mayinela incluye funciones de respuesta por voz.

Ejemplo:

.voz Hola, soy Mayinela

También puedes consultar el estado de la función:

.voz status

«La función de voz puede requerir conexión a Internet.»

---

🔄 Actualizar Mayinela

Si ya tienes Mayinela instalada y quieres descargar las últimas modificaciones:

cd ~/MayinelaV7
git pull

Después inicia nuevamente:

python main.py

---

🛑 Detener Mayinela

Para detener el proceso:

CTRL + C

En Termux puedes utilizar la combinación correspondiente de teclas para enviar "Ctrl+C".

---

🔐 Seguridad

Nunca publiques ni compartas estos datos:

- "API_ID"
- "API_HASH"
- Número de teléfono
- Código de inicio de sesión de Telegram
- Archivos ".session"
- Archivo ".env"
- Tokens o contraseñas

El proyecto utiliza ".gitignore" para evitar que archivos sensibles como ".env" y las sesiones de Telegram sean subidos accidentalmente a GitHub.

---

⚠️ Importante

Mayinela es un Userbot. Utilízalo respetando las reglas de Telegram y evita utilizarlo para spam, abuso o actividades que puedan provocar restricciones en tu cuenta.

---

📂 Estructura del proyecto

MayinelaV7/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── install.sh
├── start.sh
└── mayinela/
    ├── core/
    └── plugins/

---

🌸 Mayinela V7

Desarrollado para ejecutarse en Termux + Python + Telegram.

Repositorio oficial:

https://github.com/hirosshyeuc-creator/MayinelaV7
