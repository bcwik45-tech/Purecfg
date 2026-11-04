import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord import app_commands
from discord.ext import commands

# --- MINI SERWER HTTP DLA DARMOWEGO RENDER WEB SERVICE ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Shaders Project Bot is running!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# Uruchamiamy serwer w tle, żeby Render widział aktywny port
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
            title="<:welcome1:1567488704979669003> NOWE ZAPROSZENIE",
            description=(
                f"<:welcome2:1564005582736728156> Nowe dołączenie do **Serwera**.\n"
                f"<:welcome2:1564005582736728156> Użytkownik: {member.mention}\n"
                f"<:welcome2:1564005582736728156> Źródło: Własny link serwera (`{invite_source}`)\n"
                f"<:welcome2:1564005582736728156> Łącznie użyć vanity: `{vanity_uses}`"
            ),
            color=0x2b2d31
        )
        embed_inv.set_image(url="https://cdn.discordapp.com/attachments/1563292364414648471/1567487781641527316/zaproszenie.jpg")
        await invite_channel.send(embed=embed_inv)

# --- 2. BOOSTY ---
@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    boost_channel_id = 1563296339847282771
    if not before.premium_since and after.premium_since:
        boost_channel = after.guild.get_channel(boost_channel_id)
        if boost_channel:
            embed = discord.Embed(
                title="<:boost1:1567489688032256041> New server Boost!",
                description=(
                    f"{after.mention} **BOOST!**\n"
                    f"*thanks for boosting our server!*\n"
                    f"*Go check out our booster zone!*\n\n"
                    f"<:boost2:1567489885365997638> **Boost level**\n"
                    f"<:boost3:1567490142908719155> Server Boost level: `{after.guild.premium_tier}`\n"
                    f"<:boost4:1567490339907043388> Boost count: `{after.guild.premium_subscription_count}`"
                ),
                color=0xf47fff
            )
            embed.set_thumbnail(url=after.display_avatar.url)
            embed.set_image(url="https://cdn.discordapp.com/attachments/1563292364414648471/1567487836897415209/boost.jpg")
            embed.set_footer(text="SHADERS PROJECT")
            await boost_channel.send(embed=embed)

# --- 3. LEGIT CHECK ---
@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    
    legit_channel_id = 1566908229081108620
    if message.channel.id == legit_channel_id:
        try:
            async for m in message.channel.history(limit=10):
                if m.author == client.user:
                    await m.delete()
        except Exception:
            pass

        legit_embed = discord.Embed(
            title="☑️ JAK WYSTAWIĆ LEGIT CHECK",
            description=(
                "[☑️] Kupowałeś coś u nas? Wystaw legit check i wesprzyj renomę serwera!\n"
                "[ℹ️] Skopiuj poniższy format, uzupełnij dane i wyślij na tym kanale.\n\n"
                "📋 **WYMAGANY WZÓR**\n"
                "```+rep @osoba opis transakcji | kwota PLN | metoda```\n\n"
                "☑️ **PRZYKŁAD**\n"
                "```+rep @sprzedawca Bulletki | 30 PLN | BLIK```"
            ),
            color=0x2b2d31
        )
        legit_embed.set_image(url="https://cdn.discordapp.com/attachments/1563292364414648471/1567487784665616384/legit_check.jpg")
        legit_embed.set_footer(text="© SHADERS PROJECT - Zweryfikowane opinie")
        await message.channel.send(embed=legit_embed)
    
    await client.process_commands(message)

# --- WIDOKI I PRZYCISKI ---

class InfoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Regulamin", style=discord.ButtonStyle.secondary, custom_id="btn_regulamin")
    async def regulamin_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        reg_embed = discord.Embed(
            title="# REGULAMIN SERWERA SHADERS PROJECT",
            description=(
                "- Traktuj wszystkich z szacunkiem. Hejt, nękanie i dyskryminacja są zabronione.\n"
                "- Zachowuj kulturę wypowiedzi. Dbamy o przyjazną atmosferę, więc choć przeklinanie jest dozwolone, prosimy, by nie było nadmierne.\n"
                "- Nie promuj innych serwerów, projektów ani usług bez zgody administracji. Nieautoryzowana reklama i spam mogą skutkować ostrzeżeniem, banem lub dodaniem na blacklistę.\n"
                "- Nie publikuj treści NSFW (materiałów pornograficznych, szokujących czy nieodpowiednich dla społeczności).\n"
                "- Nie udostępniaj danych osobowych na publicznych kanałach – takich jak adresy, numery telefonu, e-maile, PESEL i podobne.\n\n"
                "Administracja może reagować na łamanie zasad. W razie pytań zgłoś się na <#1561742350986903702>."
            ),
            color=0x2b2d31
        )
        await interaction.response.send_message(embed=reg_embed, ephemeral=True)

    @discord.ui.button(label="Info Partner", style=discord.ButtonStyle.secondary, custom_id="btn_partner")
    async def partner_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        partner_embed = discord.Embed(
            title="# WYMAGANIA PARTNERSTWA",
            description="- 300 osob na serwerze\n- nie może to być shop",
            color=0x2b2d31
        )
        await interaction.response.send_message(embed=partner_embed, ephemeral=True)


class RekrutacjaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Media", style=discord.ButtonStyle.primary, custom_id="rekru_media")
    async def media_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "media", 1567494614322122832)

    @discord.ui.button(label="Administracja", style=discord.ButtonStyle.primary, custom_id="rekru