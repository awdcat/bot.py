import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

queue = []

@bot.event
async def on_ready():
    print(f'Бот {bot.user} готов воспроизводить музыку с очередью!')

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("Присоединился к голосовому каналу!")
    else:
        await ctx.send("Ты не в голосовом канале!")

@bot.command()
async def play(ctx, *, url):
    if ctx.voice_client is None:
        await ctx.invoke(bot.get_command('join'))

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'default_search': 'ytsearch',
        'source_address': '0.0.0.0',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        title = info.get('title', 'Без названия')
        queue.append((url2, title))

    await ctx.send(f'Добавлено в очередь: {title}')

    if not ctx.voice_client.is_playing():
        await play_next(ctx)

async def play_next(ctx):
    if queue:
        url2, title = queue.pop(0)
        ctx.voice_client.play(discord.FFmpegPCMAudio(url2), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
        await ctx.send(f'Сейчас играет: {title}')
    else:
        await ctx.send("Очередь пуста.")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Трек пропущен.")
    else:
        await ctx.send("Ничего не играет.")

@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Музыка на паузе.")
    else:
        await ctx.send("Сейчас ничего не воспроизводится.")

@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Продолжаем воспроизведение.")
    else:
        await ctx.send("Музыка не на паузе.")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        queue.clear()
        ctx.voice_client.stop()
        await ctx.send("Музыка остановлена и очередь очищена.")
    else:
        await ctx.send("Бот не в голосовом канале.")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Бот покинул голосовой канал.")
    else:
        await ctx.send("Бот не подключён к голосовому каналу.")

bot.run("MTM4MjQ2Mjk1MTAwNDMwNzUwNg.GQfe9N.V6_IUuGSEVsUm1Jdo3-lKxboJQhnvzbsnMH6vE")
