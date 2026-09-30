#!/data/data/com.termux/files/usr/bin/bash
set -e
pkg update -y
pkg install python ffmpeg -y
python -m pip install --upgrade pip
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
mkdir -p data sessions logs
echo "Instalación terminada. Edita .env y ejecuta: python main.py"
