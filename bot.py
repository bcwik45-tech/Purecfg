import discord
from discord.ext import commands
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- Serwer HTTP w tle utrzymujący status Online na Railway ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"COLDCFG Bot is Online!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"Serwer HTTP uruchomiony na porcie {port}")
    server.serve_forever()

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.bans = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_CHANNEL_ID = 1556280506516115466
BOOST_CHANNEL_ID = 1540358387219304592
IMG_URL = "https://i.imgur.com/rgprszrgprsz.png"

WINNER_ROLE_ID = 1556565240832073779

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

ACCEPT_ROLES = [1540359963346608168, 1540360086617063584]


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


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
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

    @discord.ui.button(label="Shop 🛒", style=discord.ButtonStyle.success, custom_id="ticket_shop")
    async def shop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "shop")

    @discord.ui.button(label="Owner 👑", style=discord.ButtonStyle.secondary, custom_id="ticket_owner")
    async def owner_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "owner")