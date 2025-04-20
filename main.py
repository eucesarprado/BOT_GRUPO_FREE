from telethon import TelegramClient, events
import os
from flask import Flask
from threading import Thread
import requests
import time

# 🔁 Servidor Flask para manter online no Railway
app = Flask('')

@app.route('/')
def home():
    return "Bot está online!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def manter_online():
    Thread(target=run_flask).start()

    def ping():
        while True:
            try:
                requests.get("https://klonechat.up.railway.app")
                print("🔁 Ping enviado para manter online.")
            except Exception as e:
                print("⚠️ Erro ao enviar ping:", e)
            time.sleep(280)

    Thread(target=ping).start()

manter_online()

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
client = TelegramClient("session", api_id, api_hash)

origens = [-1002368866066, -4686930379]
destino_id = -1002632937431
grouped_processados = set()

@client.on(events.NewMessage(chats=origens))
async def handler(event):
    msg = event.message

    if msg.grouped_id:
        if msg.grouped_id in grouped_processados:
            return
        grouped_processados.add(msg.grouped_id)

        print("📦 Álbum detectado.")
        messages = await client.get_messages(event.chat_id, limit=20, min_id=msg.id - 10)
        grupo = [m for m in messages if m.grouped_id == msg.grouped_id]
        grupo = list(reversed(grupo))
        media_files = [m.media for m in grupo if m.media]

        if media_files:
            print(f"🎯 Enviando álbum com {len(media_files)} mídias...")
            await client.send_file(destino_id, media_files)
        else:
            print("⚠️ Nenhuma mídia válida.")
    elif msg.photo or msg.video:
        print("📸 Mídia individual detectada.")
        await client.send_file(destino_id, msg.media)
    else:
        print("❌ Ignorado (sem mídia).")

client.start()
print("🤖 Bot 1 rodando com suporte a álbuns e ping automático no Railway...")
client.run_until_disconnected()
