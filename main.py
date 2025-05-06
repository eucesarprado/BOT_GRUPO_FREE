from telethon import TelegramClient, events, Button
import os
from flask import Flask
from threading import Thread, Timer
import re
import asyncio

# 🟢 Flask + Ping para manter online no Railway
app = Flask('')

@app.route('/')
def home():
    return "Bot está online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def manter_online():
    t = Thread(target=run)
    t.start()

manter_online()

# 🔐 Credenciais da API (do Railway > Variables)
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
client = TelegramClient("session", api_id, api_hash)

# 🎯 Grupos
origens = [-1001402642840, -4610792742]
destino_id = -1002569235487

# 🔁 Substituições
bot_antigo_regex = r"@\w+"
link_antigo_regex = r"https://t\.me/\S+"
bot_novo = "@BRVAZADOSVIP_BOT"
link_novo = "https://t.me/BRVAZADOSVIP_BOT"

grouped_processados = set()

# ♻️ Limpar grouped_processados periodicamente
def limpar_grouped():
    grouped_processados.clear()
    print("♻️ Limpeza de grouped_processados feita.")
    Timer(600, limpar_grouped).start()

limpar_grouped()

@client.on(events.NewMessage(chats=origens))
async def handler(event):
    try:
        msg = event.message
        texto_original = msg.message or ""

        # Substituir menções e links antigos
        nova_legenda = re.sub(bot_antigo_regex, bot_novo, texto_original)
        nova_legenda = re.sub(link_antigo_regex, link_novo, nova_legenda)


        # ÁLBUM
        if msg.grouped_id:
            if msg.grouped_id in grouped_processados:
                return
            grouped_processados.add(msg.grouped_id)

            print("📦 Álbum detectado.")
            mensagens = await client.get_messages(event.chat_id, limit=20, min_id=msg.id - 10)
            album = [m for m in mensagens if m.grouped_id == msg.grouped_id]
            album = list(reversed(album))
            media_files = [m.media for m in album if m.media]

            if media_files:
                print(f"🎯 Enviando álbum com {len(media_files)} mídias...")
                await client.send_file(
                    destino_id,
                    media_files,
                    caption=nova_legenda,
                    buttons=botao
                )
            else:
                print("⚠️ Álbum sem mídias.")
        elif msg.photo or msg.video:
            print("📸 Mídia única detectada.")
            await client.send_file(
                destino_id,
                msg.media,
                caption=nova_legenda,
                buttons=botao
            )
        else:
            print("⚠️ Ignorado (sem mídia válida).")
    except Exception as e:
        print(f"❌ Erro ao processar mensagem: {e}")

# 🚀 Iniciar bot com reconexão segura
async def main():
    print("🤖 Bot rodando com botão e ping automático no Railway!")
    await client.start()
    await client.run_until_disconnected()

client.loop.run_until_complete(main())
