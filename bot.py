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
# KONFIGURACJA ID I LINKÓW (PODMIEŃ LINKI LUB UTRZYMAJ OBECNE)
# ==========================================
COLDCFG_BANNER = "https://i.imgur.com/your_coldcfg_banner.png"        # Banner COLDCFG
COLDCFG_BOOST_BANNER = "https://i.imgur.com/your_coldcfg_boosts.png"   # Banner dla Boostów
THUMBNAIL_URL = "https://i.imgur.com/your_thumbnail.png"              # Miniaturka / memik

WELCOME_CHANNEL_ID = 123456789012345678  # ID kanału do powitań (podmień na własne ID)
BOOST_CHANNEL_ID = 123456789012345678    # ID kanału powiadomień o boostach (podmień na własne ID)

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
        super().__init__(timeout=None)

    async def create_ticket_channel(self, interaction: discord.Interaction, ticket_type: str, role_id: int):
        guild = interaction.guild
        user = interaction.user
        role = guild.get_role(role_id)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        if role:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel_name = f"ticket-{ticket_type.lower()}-{user.name}"
        channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)

        role_mention = role.mention if role else "Administration"
        embed = discord.Embed(
            title=f"🎫 Ticket - {ticket_type}",
            description=f"Witaj {user.mention}!\nOpisz swój problem lub zapytanie. Administracja ({role_mention}) niedługo Ci odpowie.",
            color=0x2b2d31
        )
        await channel.send(content=f"{user.mention} | {role_mention}", embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"✅ Twój ticket został utworzony: {channel.mention}", ephemeral=True)

    @discord.ui.button(label="Shop 🛒", style=discord.ButtonStyle.success, custom_id="btn_shop")
    async def shop_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "Shop", ROLE_SHOP_ID)

    @discord.ui.button(label="Owner 👑", style=discord.ButtonStyle.secondary, custom_id="btn_owner")
    async def owner_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "Owner", ROLE_OWNER_ID)

    @discord.ui.button(label="Support ❓", style=discord.ButtonStyle.primary, custom_id="btn_support")
    async def support_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "Support", ROLE_SUPPORT_ID)

    @discord.ui.button(label="Recruitment 📄", style=discord.ButtonStyle.danger, custom_id="btn_recruitment")
    async def recruitment_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "Recruitment", ROLE_RECRUITMENT_ID)

    @discord.ui.button(label="Partnership 🤝", style=discord.ButtonStyle.secondary, custom_id="btn_partnership")
    async def partnership_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "Partnership", ROLE_PARTNER_ID)


# ==========================================
# ON_READY
# ==========================================
@bot.event
async def on_ready():
    print(f"✅ Coldcfg Bot zalogowany jako {bot.user.name}")
    
    bot.add_view(VerifyView())
    bot.add_view(TicketSystemView())
    bot.add_view(CloseTicketView())

    try:
        synced = await bot.tree.sync()
        print(f"⚡ Zsynchronizowano {len(synced)} komend slash.")
    except Exception as e:
        print(f"❌ Błąd synchronizacji komend: {e}")


# ==========================================
# KOMENDY SETUP
# ==========================================

@bot.tree.command(name="setup_weryfikacja", description="Tworzy panel weryfikacji na kanale.")
@app_commands.checks.has_permissions(administrator=True)
async def setup_weryfikacja(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Verification",
        description="Click on verification to get access to the channels",
        color=discord.Color.green()
    )
    await interaction.channel.send(embed=embed, view=VerifyView())
    await interaction.response.send_message("✅ Panel weryfikacji został wysłany!", ephemeral=True)


@bot.tree.command(name="setup_ticket", description="Tworzy panel wszystkich ticketów na kanale.")
@app_commands.checks.has_permissions(administrator=True)
async def setup_ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎟️ Tickets",
        description=(
            "Want to place an order, need to contact the owner or staff for help?\n"
            "Click the appropriate button below to open a private channel with the administration.\n\n"
            "Please don't open the tickets without a proper reason."
        ),
        color=0xf1c40f
    )
    await interaction.channel.send(embed=embed, view=TicketSystemView())
    await interaction.response.send_message("✅ Panel ticketów został wysłany!", ephemeral=True)


# ==========================================
# KOMENDY UŻYTKOWE
# ==========================================

@bot.tree.command(name="minigame", description="Zagraj w minigrę i sprawdź swoje szczęście!")
async def minigame(interaction: discord.Interaction):
    win = random.randint(1, 35) == 1

    if win:
        embed = discord.Embed(
            title="🐱 Congratulations!",
            description=f"{interaction.user.mention}, **YOU WON!** 🎉\nYou hit the 1 in 35 chance!",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="🐱 We're sorry!",
            description=(
                f"{interaction.user.mention}, **this time you didn't win anything.** "
                f"Try your luck again tomorrow!\n\n"
                f"**Some Info:**\n"
                f"*Your chance was **1** in **35**.*\n\n"
                f"*We wish you better luck next time!*"
            ),
            color=0x2b2d31
        )

    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_image(url=COLDCFG_BANNER)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="say", description="Wyślij wiadomość w czytelnej ramce (Embed).")
@app_commands.describe(wiadomosc="Treść wiadomości do wysłania")
async def say(interaction: discord.Interaction, wiadomosc: str):
    embed = discord.Embed(
        description=wiadomosc,
        color=0x2b2d31
    )
    embed.set_footer(
        text=f"Coldcfg • Today at {interaction.created_at.strftime('%H:%M')}, Ad made by {interaction.user.display_name}"
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="bandc", description="Banuje użytkownika i tworzy raport o banie.")
@app_commands.describe(user="Użytkownik do zabanowania", reason="Powód bana")
@app_commands.checks.has_permissions(