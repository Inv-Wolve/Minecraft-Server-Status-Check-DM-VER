import discord
import os
from discord.ext import commands, tasks
from mcstatus import MinecraftServer
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
SERVER_IP = os.getenv('SERVER_IP')
USER_ID = 1234567890  # Replace with your user id

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

server_was_online = False

@bot.listen("on_ready")
async def on_ready():
    print(f'Logged in as {bot.user}')
    if not check_server_status.is_running():
        check_server_status.start()

@tasks.loop(minutes=5)
async def check_server_status():
    global server_was_online
    user = await bot.fetch_user(USER_ID)

    try:
        server = MinecraftServer.lookup(SERVER_IP)
        status = server.status()
        
        if not server_was_online:
            response = (
                f"🟢 **The Server `{SERVER_IP}` is now online!**\n"
                f"**Players Online**: {status.players.online}/{status.players.max}\n"
                f"**Ping**: {status.latency} ms"
            )
            await user.send(response)
            server_was_online = True
        else:
            response = (
                f"🟢 **The Server `{SERVER_IP}` is still online.**\n"
                f"**Players Online**: {status.players.online}/{status.players.max}\n"
                f"**Ping**: {status.latency} ms"
            )
            await user.send(response)

    except Exception as e:
        if server_was_online:
            await user.send(f"🔴 **The Server `{SERVER_IP}` is now offline.**")
            server_was_online = False
        else:
            print(f"Could not reach server {SERVER_IP}: {e}")

@bot.command()
async def mcstatus(ctx):
    await check_server_status()

bot.run(BOT_TOKEN)