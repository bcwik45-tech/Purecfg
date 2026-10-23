import os
import discord
from discord.ext import commands
from discord import app_commands

# --- KONFIGURACJA ID I LINKÓW ---
BANNER_URL = "https://cdn.discordapp.com/attachments/1563303323539476520/1563303364106649620/savage_hallowen.jpg?ex=6add2336&is=6adbd1b6&hm=83cd3b66fa3da205eb25fef7fe2d6866d35a92f367982641f9343d95d6b00cdf&"

# Kanały
SETUP_CMD_CHANNEL_ID = 1561758533446410251
TICKET_PANEL_CHANNEL_ID = 1561742350986903702
WELCOME_CHANNEL_ID = 1561740336726937660
BOOST_CHANNEL_ID = 1563296339847282771

# Rola startowa dla nowych osób
AUTO_ROLE_ID = 1540360249775493230

# Role z uprawnieniami do komend (/setup_tickets, /say, /bandc, /unbandc)
ALLOWED_COMMAND_ROLES = [1540359821323149392, 1540495893399081061]

# Role do ticketów
OWNER_ROLES = [1540359821323149392, 1540495893399081061]
PARTNER_ROLES = [1540359821323149392, 1540495893399081061]
RECRUITMENT_ROLES = [1540359905175801946]

# --- SETUP BOTA ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def has_allowed_role(user: discord.Member) -> bool:
    user_role_ids = [role.id for role in user.roles]
    return any(role_id in ALLOWED_COMMAND_ROLES for role_id in user_role_ids)

# --- PRZYCISK ZAMYKANIA TICKETA ---
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zamknij ticket ❌", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="SAVAGE × TICKET",
            description="Ticket zostanie usunięty za kilka sekund...",
            color=0x2b2d31
        )
        embed.set_image(url=BANNER_URL)
        await interaction.response.send_message(embed=embed)
        await interaction.channel.delete()

# --- SELECT MENU DO TICKETA ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Ticket Owner",
                description="Open if you have a demand to the owners",
                emoji="👑",
                value="owner"
            ),
            discord.SelectOption(
                label="Ticket Partner",
                description="Open if you want to collaborate with us.",
                emoji="🤝",
                value="partner"
            ),
            discord.SelectOption(
                label="Ticket Recruitment",
                description="Open if you want to join our team",
                emoji="📝",
                value="recruitment"
            ),
        ]
        super().__init__(placeholder="➔ Select category...", min_values=1, max_values=1, options=options, custom_id="ticket_select_menu")

    async def callback(self, interaction: discord.Interaction):
        #Zapobieganie podwójnemu tworzeniu ticketów
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        category_name = self.values[0]
        
        ping_roles = []
        emoji_prefix = "🎫"

        if category_name == "owner":
            ping_roles = OWNER_ROLES
            emoji_prefix = "👑"
        elif category_name == "partner":
            ping_roles = PARTNER_ROLES
            emoji_prefix = "🤝"
        elif category_name == "recruitment":
            ping_roles = RECRUITMENT_ROLES
            emoji_prefix = "📝"

        channel_name = f"{emoji_prefix}・ticket-{interaction.user.name}"
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        for r_id in ping_roles:
            role = guild.get_role(r_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)

        pings_formatted = " ".join([f"<@&{r_id}>" for r_id in ping_roles])
        
        embed = discord.Embed(
            title=f"SAVAGE × {category_name.upper()}",
            description="Cześć witaj w savage opisz swoją sytuację",
            color=0x2b2d31
        )
        embed.set_image(url=BANNER_URL)

        await ticket_channel.send(content=f"{interaction.user.mention} {pings_formatted}", embed=embed, view=CloseTicketView())
        await interaction.followup.send(f"Stworz