import discord
from discord.ext import commands
from gtts import gTTS
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# ID пользователей для озвучки
TARGET_USER_IDS = [423444867021275146, 449996138590765086] #449996138590765086

# Настройки
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

TEMP_AUDIO_DIR = "temp_audio"
if not os.path.exists(TEMP_AUDIO_DIR):
    os.makedirs(TEMP_AUDIO_DIR)


@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} запущен и готов к работе!')


@bot.event
async def on_message(message):
    # Не обрабатываем свои сообщения
    if message.author == bot.user:
        return
    # ID текстового канала, откуда нужно озвучивать сообщения
    TARGET_TEXT_CHANNEL_ID = [1497293587552145498,1497249996490408198]  # <-- ЗАМЕНИТЕ НА ID ВАШЕГО КАНАЛА!

    if message.author.id in TARGET_USER_IDS and message.channel.id in TARGET_TEXT_CHANNEL_ID:
        voice_client = discord.utils.get(bot.voice_clients, guild=message.guild)

        # Проверяем: бот в голосе и автор в том же канале
        if voice_client and message.author.voice and voice_client.channel == message.author.voice.channel:
            print(f"🔊 Озвучиваю: {message.content[:50]}...")
            try:
                tts = gTTS(text=message.content, lang='ru')
                audio_filename = f"{TEMP_AUDIO_DIR}/{message.id}.mp3"
                tts.save(audio_filename)

                audio_source = discord.FFmpegPCMAudio(audio_filename)
                voice_client.play(audio_source)

                while voice_client.is_playing():
                    await asyncio.sleep(0.5)

                os.remove(audio_filename)
                print(f"✅ Готово")
            except Exception as e:
                print(f"❌ Ошибка: {e}")

    # ⚠️ ВАЖНО: эта строка должна быть здесь, после всей логики озвучки
    await bot.process_commands(message)


@bot.command()
async def join(ctx):
    """Бот заходит в ваш голосовой канал"""
    if not ctx.author.voice:
        await ctx.send("❌ Вы не в голосовом канале!")
        return

    channel = ctx.author.voice.channel

    if ctx.voice_client and ctx.voice_client.channel == channel:
        await ctx.send("🤖 Я уже в этом канале!")
        return

    if ctx.voice_client:
        await ctx.voice_client.disconnect()

    await channel.connect()
    await ctx.send(f"🔊 Зашёл в {channel.name}")


@bot.command()
async def leave(ctx):
    """Бот выходит из голосового канала"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("🔇 Вышел из канала")
    else:
        await ctx.send("❌ Бот не в голосовом канале!")


@bot.command()
async def ping(ctx):
    await ctx.send("Понг! Бот работает.")


if __name__ == "__main__":
    if TOKEN is None:
        print("❌ Токен не найден!")
    else:
        bot.run(TOKEN)