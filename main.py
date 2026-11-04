import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord import app_commands
from discord.ext import commands

# --- SERWER HTTP DLA RENDER & UPTIMEROBOT ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Shaders Project Bot is running!")
        
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- KONFIGURACJA BOTA DISCORDA ---
intents = discord.Intents.all()

class ShadersBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("Komendy slash zostały zsynchronizowane!")

client = ShadersBot()

@client.event
async def on_ready():
    print(f"Zalogowano jako {client.user}!")

# --- 1. POWITANIA (WELCOME) & ZAPROSZENIA ---
@client.event
async def on_member_join(member: discord.Member):
    welcome_channel_id = 1561740336726937660
    invite_channel_id = 1566902544406421615

    welcome_channel = member.guild.get_channel(welcome_channel_id)
    if welcome_channel:
        embed = discord.Embed(
            title="<:welcome1:1567488704979669003> NOWY UŻYTKOWNIK",
            description=(
                f"<:welcome2:1564005582736728156> Witaj, {member.mention}! Miło że wpadłeś jesteś naszą **{member.guild.member_count}** osobą!\n"
                f"<:welcome2:1564005582736728156> Pobierz **najlepsze dodatki do fivem** właśnie tutaj!\n"
                f"<:welcome2:1564005582736728156> **Życzymy** miłego pobytu na **SHADERS PROJECT**"
            ),
            color=0x2b2d31
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1563292364414648471/1567487836457009162/welcome.jpg")
        await welcome_channel.send(embed=embed)

    invite_channel = member.guild.get_channel(invite_channel_id)
    if invite_channel:
        invite_source = "discord.gg/shadersproject"
        vanity_uses = 0
        try:
            vanity = await member.guild.vanity_invite()
            if vanity:
                vanity_uses = vanity.uses
        except Exception:
            pass

        embed_inv = discord.Embed(
            title="<:welcome1:156748