import discord
from discord.ext import commands, tasks
from discord import app_commands
import random
import asyncio
import os
from datetime import date

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

COLDCFG_BANNER = "https://i.imgur.com/your_coldcfg_banner.png"
MINIGAME_BANNER = "TUTAJ_WKLEJ_LINK_DO_OBRAZKA_Z_NAPISEM_COLDCFG"
COLDCFG_BOOST_BANNER = "https://i.imgur.com/your_coldcfg_boosts.png"
THUMBNAIL_URL = "https://i.imgur.com/your_thumbnail.png"

# ==========================================
# ID KANAŁÓW POWITAŃ I BOOSTÓW
# ==========================================
WELCOME_CHANNEL_ID = 1556280506516115466
BOOST_CHANNEL_ID = 1540358387219304592

MINIGAME_CHANNEL_ID = 1556566161653764157
MINIGAME_WIN_ROLE_ID = 1556565240832073779

ROLE_VERIFIED_ID = 1540360249775493230

# ==========================================
# LISTY RÓL DLA POSZCZEGÓLNYCH TICKETÓW
# ==========================================
ROLES_OWNER = [1540359821323149392, 1540495893399081061]
ROLES_SHOP = [1540359821323149392]
ROLES_SUPPORT = [1540360086617063584, 1540359905175801946, 1556062543963750400, 1540495893399081061, 1540359821323149392]
ROLES_RECRUITMENT = [1540359821323149392, 1540495893399081061, 1556062543963750400, 1540359905175801946]
ROLES_PARTNER = [1540359821323149392, 1540495893399081061]

# ==========================================
# ID KATEGORII NA DISCORDZIE DLA TICKETÓW
# ==========================================
CATEGORY_OWNER_ID = 1556300080355606608
CATEGORY_SHOP_ID = 1556300130892906506
CATEGORY_SUPPORT_ID = 1556300180624769105
CATEGORY_RECRUITMENT_ID = 1556300236526329936
CATEGORY_PARTNER_ID = 1556383124424892606

# Słownik do śledzenia cooldownu minigry (user_id -> data)
minigame_cooldowns = {}


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        role = interaction.guild.get_role(ROLE_VERIFIED_ID)
        if role:
            if role in interaction.user.roles:
                await interaction.followup.send("❌ Jesteś już zweryfikowany!", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.followup.send("✅ Pomyślnie zweryfikowano! Otrzymałeś dostęp do kanałów.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Błąd: Nie znaleziono roli do weryfikacji.", ephemeral=True)


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
        super().__init__(timeout=None)

    async def create_ticket_channel(self, interaction: discord.Interaction, ticket_type: str, role_ids: list, category_id: int, emoji: str):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        user = interaction.user
        category = guild.get_channel(category_id)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        roles_mentions = []
        for r_id in role_ids:
            role = guild.get_role(r_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                roles_mentions.append(role.mention)

        channel_name = f"{emoji}-{ticket_type.lower()}-{user.name}"
        target_category = category if isinstance(category, discord.CategoryChannel) else None

        channel = await guild.create_text_channel(
            name=channel_name, 
            overwrites=overwrites, 
            category=target_category
        )

        role_ping_str = " ".join(roles_mentions) if roles_mentions else "@here"
        embed_color = 0xf1c40f if ticket_type == "Partnership" else 0x3498db

        embed = discord.Embed(
            title=f"🎫 Ticket - {ticket_type}",
            description