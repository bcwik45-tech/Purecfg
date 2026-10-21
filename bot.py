import os
import discord
from discord.ext import commands
from discord import app_commands

# --- KONFIGURACJA POLISHCFG ---
EMBED_COLOR = 0x2B2D31
# Tutaj podmień na bezpośredni link do Twojego GIF-a / Logo
GIF_URL = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjEx.../giphy.gif"
FOOTER_TEXT = "POLISHCFG • Wszelkie prawa zastrzeżone"

# ID Kanałów
VERIFY_CHANNEL_ID = 1556706704073424896  # Kanał weryfikacji
TICKET_CHANNEL_ID = 1561742350986903702  # Kanał ticketów
VERIFIED_ROLE_ID = 123456789012345680   # Wpisz ID roli po weryfikacji

class PolishBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        print("Synchronizacja komend slash...")
        await self.tree.sync()
        print("Komendy slash zsynchronizowane!")

bot = PolishBot()

# --- PANEL WERYFIKACJI ---
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.green, custom_id="verify_btn", emoji="✅")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(VERIFIED_ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Pomyślnie zweryfikowano na serwerze POLISHCFG!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Nie znaleziono skonfigurowanej roli weryfikacyjnej.", ephemeral=True)

# --- PANEL TICKETÓW (ROZWIJANA LISTA KATEGORII) ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Ticket Owner", description="Open if you have a demand to the owners.", emoji="👑"),
            discord.SelectOption(label="Ticket Shop", description="Open if you want to buy something.", emoji="🛒"),
            discord.SelectOption(label="Ticket Support", description="Open if you need any help.", emoji="🛠️"),
            discord.SelectOption(label="Ticket Partner", description="Open if you want to collaborate with us.", emoji="🤝"),
        ]
        super().__init__(placeholder="Select category...", min_values=1, max_values=1, custom_id="ticket_select_category", options=options)

    async def callback(self, interaction: discord.Interaction):
        category_name = self.values[0]
        guild = interaction.guild
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        clean_cat = category_name.lower().replace(' ', '-')
        channel_name = f"{clean_cat}-{interaction.user.name}"
        ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
        
        embed = discord.Embed(
            title=f"POLISHCFG • {category_name}",
            description=f"Witaj {interaction.user.mention}!\nKategoria: **{category_name}**.\nOpisz swój problem, a administracja odpowie najszybciej jak to możliwe.",
            color=EMBED_COLOR
        )
        if GIF_URL.startswith("http"):
            embed.set_image(url=GIF_URL)
        embed.set_footer(text=FOOTER_TEXT)
        
        await ticket_channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Stworzono kanał zgłoszenia: {ticket_channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# --- KOMENDY SETUP ---
@bot.tree.command(name="setup_weryfikacja", description="Wysyła panel weryfikacyjny na kanał verification")
async def setup_weryfikacja(interaction: discord.Interaction):
    channel = bot.get_channel(VERIFY_CHANNEL_ID) or interaction.channel
    embed = discord.Embed(
        title="POLISHCFG • Weryfikacja",
        description="Kliknij poniższy przycisk, aby zweryfikować swoje konto i uzyskać dostęp do serwera.",
        color=EMBED_COLOR
    )
    if GIF_URL.startswith("http"):
        embed.set_image(url=GIF_URL)
    embed.set_footer(text=FOOTER_TEXT)
    
    await channel.send(embed=embed, view=VerifyView())
    await interaction.response.send_message(f"✅ Panel weryfikacji wysłany na {channel.mention}!", ephemeral=True)

@bot.tree.command(name="setup_tickets", description="Wysyła panel ticketów z rozwijaną listą")
async def setup_tickets(interaction: discord.Interaction):
    channel = bot.get_channel(TICKET_CHANNEL_ID) or interaction.channel
    
    embed = discord.Embed(
        title="Tickets",
        description=(
            "**Ticket Owner**\n*Open if you have a demand to the owners.*\n\n"
            "**Ticket Shop**\n*Open if you want to buy something.*\n\n"
            "**Ticket Support**\n*Open if you need any help.*\n\n"
            "**Ticket Partner**\n*Open if you want to collaborate with us.*\n\n"
            "For any issues, text us in #chat"
        ),
        color=EMBED_COLOR
    )
    if GIF_URL.startswith("http"):
        embed.set_image(url=GIF_URL)
    embed.set_footer(text=FOOTER_TEXT)
    
    await channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message(f"✅ Panel ticketów wysłany na {channel.mention}!", ephemeral=True)

# --- KOMENDY MODERACYJNE ---
@bot.tree.command(name="bandc", description="Banuje użytkownika na serwerze POLISHCFG")
@app_commands.checks.has_permissions(ban_members=True)
async def bandc(interaction: discord.Interaction, member