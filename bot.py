import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import os

# Uprawnienia bota (Intents)
intents = discord.Intents.default()
intents.members = True          # Wymagane do weryfikacji, powitań i boostów
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# KONFIGURACJA ID I LINKÓW (UZUPEŁNIJ LINKI DO GRAFIK)
# ==========================================
COLDCFG_BANNER = "https://i.imgur.com/your_coldcfg_banner.png"        # Banner COLDCFG
COLDCFG_BOOST_BANNER = "https://i.imgur.com/your_coldcfg_boosts.png"   # Banner dla Boostów
THUMBNAIL_URL = "https://i.imgur.com/your_thumbnail.png"              # Miniaturka / memik

WELCOME_CHANNEL_ID = 123456789012345678  # ID kanału do powitań (podmień na własne)
BOOST_CHANNEL_ID = 123456789012345678    # ID kanału powiadomień o boostach (podmień na własne)

# ID ROLI DO WERYFIKACJI
ROLE_VERIFIED_ID = 1540360249775493230

# ID RÓL DLA TICKETÓW
ROLE_SHOP_ID = 1556300130892906506
ROLE_RECRUITMENT_ID = 1556300236526329936
ROLE_OWNER_ID = 1556300080355606608
ROLE_SUPPORT_ID = 1556300180624769105
ROLE_PARTNER_ID = 1556383124424892606


# ==========================================
# 1. WERYFIKACJA (PRZYCISK & VIEW)
# ==========================================
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_VERIFIED_ID)
        if role:
            if role in interaction.user.roles:
                await interaction.response.send_message("❌ Jesteś już zweryfikowany!", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("✅ Pomyślnie zweryfikowano! Otrzymałeś dostęp do kanałów.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Błąd: Nie znaleziono roli do weryfikacji.", ephemeral=True)


# ==========================================
# 2. SYSTEM TICKETÓW (PRZYCISKI & VIEW)
# ==========================================
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket 🔒", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Ten ticket zostanie zamknięty za 5 sekund...")
        await asyncio.sleep(5)
        await interaction.channel.delete()


class TicketSystemView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout