import os
import discord
from discord.ext import commands
from discord import app_commands

# --- KONFIGURACJA BRANDINGU POLISHCFG ---
EMBED_COLOR = 0x2B2D31
BRAND_ICON_URL = "https://cdn.discordapp.com/attachments/1200000000000000000/1200000000000000000/polishcfg_logo.png"  # Twój link do logo
FOOTER_TEXT = "POLISHCFG • Wszelkie prawa zastrzeżone"

# ID Kanałów (Zastąp własnymi ID kanałów z serwera!)
VERIFY_CHANNEL_ID = 123456789012345678  # Kanał gdzie ma być panel weryfikacji
TICKET_CHANNEL_ID = 123456789012345679  # Kanał gdzie ma być panel ticketów
VERIFIED_ROLE_ID = 123456789012345680   # Rola przyznawana po weryfikacji

class PolishBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Wymuszenie wyczyszczenia i natychmiastowej synchronizacji komend
        print("Czyszczenie i synchronizacja komend slash...")
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
            await interaction.response.send_message("✅ Pomyślnie zweryfikowano! Uzyskano dostęp do serwera POLISHCFG.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Błąd: Nie znaleziono roli weryfikacyjnej.", ephemeral=True)

# --- PANEL TICKETÓW ---
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Otwórz Ticket", style=discord.ButtonStyle.blurple, custom_id="ticket_btn", emoji="📩")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel_name = f"ticket-{interaction.user.name}"
        ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
        
        embed = discord.Embed(
            title="POLISHCFG • Pomoc i Wsparcie",
            description=f"Witaj {interaction.user.mention}!\nOpisz swój problem, a nasza obsługa odpow