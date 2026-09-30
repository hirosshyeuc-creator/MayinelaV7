🌸 Mayinela V7
Userbot de Telegram para Termux, desarrollado en Python.
📱 Instalación en Termux
1. Instalar Termux
Se recomienda utilizar una versión actualizada de Termux.
2. Actualizar paquetes
pkg update && pkg upgrade -y
3. Instalar dependencias básicas
pkg install git python unzip -y
4. Clonar el repositorio
git clone https://github.com/hirosshyeuc-creator/MayinelaV7.git
5. Entrar en la carpeta
cd MayinelaV7
6. Instalar las dependencias de Python
pip install -r requirements.txt
7. Configurar las credenciales
Copia el archivo de ejemplo:
cp .env.example .env
Edita .env:
nano .env
Introduce tus propias credenciales de Telegram.
⚠️ Nunca publiques tu archivo .env, API_HASH, tokens ni códigos de inicio de sesión.
8. Iniciar Mayinela
python main.py
Durante el primer inicio, Telegram puede solicitar el código de inicio de sesión.
🔄 Actualizar Mayinela
Desde la carpeta del proyecto:
git pull
Después puedes iniciar nuevamente:
python main.py
🌸 Comando principal
Una vez iniciado el userbot:
.menu
Muestra el menú principal y las funciones disponibles.
🔐 Seguridad
No compartas públicamente:
API_ID
API_HASH
números de teléfono
códigos de Telegram
archivos .session
archivo .env
