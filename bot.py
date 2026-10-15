import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- NATYCHMIASTOWY SERWER HTTP DLA RAILWAY ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Uruchamiamy port w pierwszej kolejności, żeby Railway od razu widział ruch
threading.Thread(target=run_http_server, daemon=True).start()
# ----------------------------------------------

import discord
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.bans = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_CHANNEL_ID = 1556280506516115466
BOOST_CHANNEL_ID = 1540358387219304592
MINIGAME_CHANNEL_ID = 0  # <--- Wpisz tutaj ID kanału dla przypomnień o minigrze
IMG_URL = "https://cdn.discordapp.com/attachments/1548988126452781137/1559839172653490246/coldcfg.gif"
WINNER_ROLE_ID = 1556565240832073779
ACCEPT_ROLE_ID = 1560349104893206568

TICKET_CATEGORIES = {
    "shop": 1556300130892906506,
    "owner": 1556300080355606608,
    "support": 1556300180624769105,
    "recruitment": 1556300236526329936,
    "partner": 1556383124424892606
}

TICKET_EMOJIS = {
    "shop": "🛒",
    "owner": "👑",
    "support": "❓",
    "recruitment": "📄",
    "partner": "🤝"
}

TICKET_ROLES = {
    "shop": [1540359821323149392],
    "owner": [1540359821323149392, 1540495893399081061],
    "support": [1540359821323149392, 1540495893399081061, 1556062543963750400, 1540359905175801946, 1540360086617063584],
    "recruitment": [1540359821323149392, 1540495893399081061, 1556062543963750400, 1540359905175801946],
    "partner": [1540359821323149392, 1540495893399081061]
}


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zamknij ticket 🔒", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Zamykanie i usuwanie ticketu...", ephemeral=True)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"Błąd przy zamykaniu ticketu: {e}")


class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Owner", description="Ticket with a matter for the config owners", emoji="👑", value="owner"),
            discord.SelectOption(label="Shop", description="Ticket for purchase an item from our store", emoji="🛒", value="shop"),
            discord.SelectOption(label="Support", description="Support ticket for help in our config server", emoji="❓", value="support"),
            discord.SelectOption(label="Recruitment", description="Application or recruitment matters", emoji="📄", value="recruitment"),
            discord.SelectOption(label="Partner", description="Ticket for partnership", emoji="🤝", value="partner")
        ]
        super().__init__(placeholder="Select category...", min_values=1, max_values=1, options=options, custom_id="persistent_ticket_select")

    async def callback(self, interaction: discord.Interaction):
        ticket_type = self.values[0]
        guild = interaction.guild
        category_id = TICKET_CATEGORIES.get(ticket_type)
        category = guild.get_channel(category_id) if category_id else None
        allowed_role_ids = TICKET_ROLES.get(ticket_type, [])
        emoji = TICKET_EMOJIS.get(ticket_type, "🎫")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        for r_id in allowed_role_ids:
            role = guild.get_role(r_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        channel_name = f"{emoji}-ticket-{ticket_type}-{interaction.user.name}".lower()
        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

        role_pings = " ".join([f"<@&{r_id}>" for r_id in allowed_role_ids])

        embed = discord.Embed(
            title=f"Ticket: {ticket_type.upper()}",
            description=f"Witaj <@!{interaction.user.id}>!\nAdministracja wkrótce odpowie na Twoje zgłoszenie.\n\nAby zamknąć ten kanał, kliknij przycisk poniżej.",
            color=0x2b2d31
        )
        await ticket_channel.send(content=f"{role_pings} <@!{interaction.user.id}>", embeds=[embed], view=CloseTicketView())
        await interaction.response.send_message(f"Utworzono Twój ticket: {ticket_channel.mention}", ephemeral=True)


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.success, emoji="✅", custom_id="verify_btn_new")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ACCEPT_ROLE_ID)
        if not role:
            return await interaction.response.send_message("Nie znaleziono roli weryfikacji.", ephemeral=True)
        
        if role in interaction.user.roles:
            await interaction.response.send_message("Jesteś już zweryfikowany!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("Pomyślnie zweryfikowano!", ephemeral=True)


@tasks.loop(hours=24)
async def minigame_daily_reminder():
    if MINIGAME_CHANNEL_ID == 0:
        return
    channel = bot.get_channel(MINIGAME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="Daily reminder 🦦",
            description="Use /minigame to win an award! Booster gets something more!",
            color=0x2b2d31
        )
        await channel.send(embed=embed)


@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}!")
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
    if not minigame_daily_reminder.is_running():
        minigame_daily_reminder.start()
    try:
        synced = await bot.tree.sync()
        print(f"Zsynchronizowano {len(synced)} komend slash.")
    except Exception as e:
        print(e)


@bot.event
async def on_member_join(member: discord.Member):
    channel = member.guild.get_channel