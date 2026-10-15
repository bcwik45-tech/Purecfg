import os
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
MINIGAME_CHANNEL_ID = 0
IMG_URL = "https://cdn.discordapp.com/attachments/1548988126452781137/1560367951020953651/coldcfg2.gif"
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
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=