import discord
from discord import app_commands
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- ID RÓL I KANAŁÓW ---
VERIFY_ROLE_ID = 1540360249775493230
WELCOME_CH = 1556280506516115466
GLOBAL_INFO_CH = 1540356981238530098
REVIEWS_CH = 1561742557019373618

# Kategorie ticketów
TICKET_CATEGORIES = {
    "owner": 1556300080355606608,
    "shop": 1556300130892906506,
    "support": 1556300180624769105,
    "recruitment": 1556300236526329936,
    "partnership": 1556383124424892606
}

# Dostęp ról do ticketów
TICKET_ROLES = {
    "owner": 1540359821323149392,
    "shop": 1540359821323149392,
    "support": 1561785358683996351,
    "recruitment": 1561785358683996351,
    "partnership": 1540359821323149392
}

# --- BANERY ---
PRICE_LIST_BANNER = "https://cdn.discordapp.com/attachments/1556342431903911966/1561450000000000001/Cennik_SpiderMafia.png"
SUSANO_BANNER = "https://cdn.discordapp.com/attachments/1556342431903911966/1561450000000000002/Mroczny_baner_FIVEM_SUSANO.png"
AMBANI_BANNER = "https://cdn.discordapp.com/attachments/1556342431903911966/1561450000000000003/fivem_ambani.png"
KEYSER_BANNER = "https://cdn.discordapp.com/attachments/1556342431903911966/1561450000000000004/Czerwony_neonowy_baner_FiveM_Keyser.png"
REDENGINE_BANNER = "https://cdn.discordapp.com/attachments/1556342431903911966/1561450000000000005/Redengine.jpg"
VPN_BANNER = "https://cdn.discordapp.com/attachments/1556342431903911966/1561450000000000006/ipvvanish_banner.png"
BUNDLE_MAIN_BANNER = "https://cdn.discordapp.com/attachments/1556342431903911966/1561450000000000007/bundle_banner.png"
STEAM_BANNER = "https://cdn.discordapp.com/attachments/1556342431903911966/1561450000000000008/steam_banner.png"
DISCORD_BANNER = "https://cdn.discordapp.com/attachments/1556342431903911966/1561450000000000009/discord_banner.png"
CS_MAIN_BANNER = "https://cdn.discordapp.com/attachments/1556342431903911966/1561450000000000010/cs2_spidermafia.jpg"
MEMESENSE_BANNER = "https://cdn.discordapp.com/attachments/1556342431903911966/1561450000000000011/memesense_banner.png"


# --- 1. WERYFIKACJA I POWITANIA ---
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.green, emoji="✅", custom_id="verify_button")
    async def verify_callback(self, inter: discord.Interaction, button: discord.ui.Button):
        role = inter.guild.get_role(VERIFY_ROLE_ID)
        if role in inter.user.roles:
            await inter.response.send_message("Jesteś już zweryfikowany!", ephemeral=True)
        else:
            await inter.user.add_roles(role)
            await inter.response.send_message("Pomyślnie przeszedłeś weryfikację w **Spidermafia**!", ephemeral=True)

@bot.event
async def on_member_join(member: discord.Member):
    channel = member.guild.get_channel(WELCOME_CH)
    if channel:
        embed = discord.Embed(
            title="Witaj w Spidermafia!",
            description=f"Witaj {member.mention}! Cieszymy się, że do nas dołączyłeś. Przejdź do kanału weryfikacji, aby uzyskać pełny dostęp do serwera.",
            color=discord.Color.from_rgb(180, 0, 0)
        )
        await channel.send(embed=embed)

@bot.tree.command(name="weryfikacja", description="Wysyła panel weryfikacyjny")
@app_commands.checks.has_permissions(administrator=True)
async def weryfikacja(inter: discord.Interaction):
    embed = discord.Embed(
        title="Weryfikacja Spidermafia",
        description="Kliknij przycisk poniżej, aby zweryfikować swoje konto.",
        color=discord.Color.from_rgb(180, 0, 0)
    )
    await inter.channel.send(embed=embed, view=VerifyView())
    await inter.response.send_message("Wysłano panel weryfikacji.", ephemeral=True)


# --- 2. TICKETY ---
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zamknij Ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket_btn")
    async def close_callback(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.send_message("Zamykanie ticketa...", ephemeral=True)
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=3))
        await inter.channel.delete()

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Ticket Owner", description="Open if you have a demand to the owners.", emoji="👑"),
            discord.SelectOption(label="Ticket Shop", description="Open if you want to buy something.", emoji="🛒"),
            discord.SelectOption(label="Ticket Support", description="Open if you need any help.", emoji="🎫"),
            discord.SelectOption(label="Ticket Recruitment", description="Open if you want to join us.", emoji="📋"),
            discord.SelectOption(label="Ticket Partner", description="Open if you want to collaborate with us.", emoji="🤝")
        ]
        super().__init__(placeholder="Select category...", min_values=1, max_values=1, options=options)

    async def callback(self, inter: discord.Interaction):
        val = self.values[0]
        guild = inter.guild
        key = "owner" if "Owner" in val else "shop" if "Shop" in val else "support" if "Support" in val else "recruitment" if "Recruitment" in val else "partnership"
        
        category = guild.get_channel(TICKET_CATEGORIES[key])
        role = guild.get_role(TICKET_ROLES[key])

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            inter.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        channel = await guild.create_text_channel(name=f"ticket-{inter.user.name}", category=category, overwrites=overwrites)
        embed = discord.Embed(
            title=f"Ticket: {val}",
            description=f"Witaj {inter.user.mention}! Opisz swoją sprawę, administracja wkrótce odpowie.",
            color=discord.Color.from_rgb(180, 0, 0)
        )
        await channel.send(content=f"{role.mention} {inter.user.mention}", embed=embed, view=CloseTicketView())
        await inter.response.send_message(f"Utworzono ticket: {channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

@bot.tree.command(name="tickets", description="Wysyła panel ticketów")
@app_commands.checks.has_permissions(administrator=True)
async def tickets(inter: discord.Interaction):
    embed = discord.Embed(title="Tickets", description="Wybierz kategorię ticketa z menu poniżej.", color=discord.Color.dark_embed())
    await inter.channel.send(embed=embed, view=TicketView())
    await inter.response.send_message("Wysłano panel ticketów.", ephemeral=True)


# --- 3. GLOBAL INFO & REVIEWS ---
@bot.tree.command(name="globalinfo", description="Wyświetla ogólne informacje i regulamin Spidermafia")
@app_commands.checks.has_permissions(administrator=True)
async def globalinfo(inter: discord.Interaction):
    embed = discord.Embed(
        title="Spidermafia — Global Info",
        description="**Regulamin (§1-§8)**, **Płatności (BLIK / PSC)** oraz **Partnership** są dostępne na tym kanale.",
        color=discord.Color.from_rgb(180, 0, 0)
    )
    await inter.channel.send(embed=embed)
    await inter.response.send_message("Wysłano Global Info.", ephemeral=True)

@bot.tree.command(name="reviews", description="Informacje o systemie recenzji")
@app_commands.checks.has_permissions(administrator=True)
async def reviews(inter: discord.Interaction):
    embed = discord.Embed(
        title="Spidermafia — Reviews",
        description=f"Sprawdź lub wystaw opinię na kanale <#{REVIEWS_CH}>!",
        color=discord.Color.from_rgb(180, 0, 0)
    )
    await inter.channel.send(embed=embed)
    await inter.response.send_message("Wysłano panel recenzji.", ephemeral=True)


# --- 4. MODERACJA (/bandc, /unbandc) ---
@bot.tree.command(name="bandc", description="Banuje użytkownika")
@app_commands.checks.has_permissions(administrator=True)
async def bandc(inter: discord.Interaction, member: discord.Member, reason: str = "Brak powody"):
    await member.ban(reason=reason)
    await inter.response.send_message(f"Zbanowano {member.mention}. Powód: {reason}", ephemeral=True)

@bot.tree.command(name="unbandc", description="Odbanowuje użytkownika po ID")
@app_commands.checks.has_permissions(administrator=True)
async def unbandc(inter: discord.Interaction, user_id: str):
    user = await bot.fetch_user(int(user_id))
    await inter.guild.unban(user)
    await inter.response.send_message(f"Odbanowano użytkownika {user.name}.", ephemeral=True)


# --- 5. SKLEP: /cheats (FiveM) ---
class CheatsSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Susano / Susano Lite", description="See price", emoji=discord.PartialEmoji.from_str("<:susano:1561762163822170243>")),
            discord.SelectOption(label="Ambani", description="See price", emoji=discord.PartialEmoji.from_str("<:ambani:1561761766856204368>")),
            discord.SelectOption(label="Keyser Internal / External", description="See price", emoji=discord.PartialEmoji.from_str("<:keyser:1561761530612162650>"))
        ]
        super().__init__(placeholder="❌ × Wybierz ofertę z listy", min_values=1, max_values=1, options=options)

    async def callback(self, inter: discord.Interaction):
        val = self.values[0]
        if val == "Susano / Susano Lite":
            desc = "``` SUSANO ```\n\n│ ***PRICE LIST*** 💸\n\n│ • 📅 **Week** » `55 PLN` 💸\n│ • 📅 **Month** » `75 PLN` 💸\n│ • 📅 **3 Months** » `110 PLN` 💸\n│ • 📅 **Lifetime** » `150 PLN` 💸"
            embed = discord.Embed(description=desc, color=discord.Color.from_rgb(180, 0, 0))
            embed.set_image(url=SUSANO_BANNER)
            await inter.response.send_message(embed=embed, ephemeral=True)
        elif val == "Ambani":
            desc = "``` AMBANI ```\n\n│ ***PRICE LIST*** 💸\n\n│ • 📅 **Week** » `42 PLN` 💸\n│ • 📅 **Month** » `60 PLN` 💸\n│ • 📅 **Lifetime** » `135 PLN` 💸"
            embed = discord.Embed(description=desc, color=discord.Color.from_rgb(180, 0, 0))
            embed.set_image(url=AMBANI_BANNER)
            await inter.response.send_message(embed=embed, ephemeral=True)
        elif val == "Keyser Internal / External":
            desc = "``` KEYSER INTERNAL ```\n\n│ ***PRICE LIST*** 💸\n\n│ • 📅 **1 Day** » `25 PLN` 💸\n│ • 📅 **Week** » `47 PLN` 💸\n│ • 📅 **Month** » `64 PLN` 💸\n│ • 📅 **Lifetime** » `155 PLN` 💸\n\n``` KEYSER EXTERNAL ```\n\n│ ***PRICE LIST*** 💸\n\n│ • 📅 **Month** » `90 PLN` 💸\n│ • 📅 **Lifetime** » `177 PLN` 💸"
            embed = discord.Embed(description=desc, color=discord.Color.from_rgb(180, 0, 0))
            embed.set_image(url=KEYSER_BANNER)
            await inter.response.send_message(embed=embed, ephemeral=True)

class CheatsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CheatsSelect())

@bot.tree.command(name="cheats", description="Lista i cennik produktów FiveM")
@app_commands.checks.has_permissions(administrator=True)
async def cheats(inter: discord.Interaction):
    desc = "``` 🛒 SPIDERMAFIA PRODUCTS × FIVEM PRODUCTS ```\n\n**Cheats available from us:**\n• <:susano:1561762163822170243> **Susano / Susano Lite**\n• <:ambani:1561761766856204368> **Ambani**\n• <:keyser:1561761530612162650> **Keyser Internal / External**"
    embed = discord.Embed(description=desc, color=discord.Color.dark_embed())
    embed.set_image(url=PRICE_LIST_BANNER)
    await inter.response.send_message(embed=embed, view=CheatsView())


# --- 6. SKLEP: /spoofer ---
class SpooferSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Red Engine", description="See price", emoji=discord.PartialEmoji.from_str("<:redengine:1561770287832244226>")),
            discord.SelectOption(label="Echo.Fun", description="See price", emoji=discord.PartialEmoji.from_str("<:echo:1561770287832244225>"))
        ]
        super().__init__(placeholder="❌ × Wybierz ofertę z listy", min_values=1, max_values=1, options=options)

    async def callback(self, inter: discord.Interaction):
        val = self.values[0]
        if val == "Red Engine":
            desc = "``` RED ENGINE ```\n\n│ ***PRICE LIST*** 💸\n\n│ • 📅 **Week** » `40 PLN` 💸\n│ • 📅 **Month** » `70 PLN` 💸\n│ • 📅 **Lifetime** » `177 PLN` 💸"
            embed = discord.Embed(description=desc, color=discord.Color.from_rgb(180, 0, 0))
            embed.set_image(url=REDENGINE_BANNER)
            await inter.response.send_message(embed=embed, ephemeral=True)
        elif val == "Echo.Fun":
            desc = "``` ECHO.FUN ```\n\n│ ***PRICE LIST*** 💸\n\n│ • 📅 **Week** » `21.50 PLN` 💸\n│ • 📅 **Month** » `40 PLN` 💸\n│ • 📅 **Lifetime** » `80 PLN` 💸"
            embed = discord.Embed(description=desc, color=discord.Color.from_rgb(180, 0, 0))
            embed.set_image(url=PRICE_LIST_BANNER)
            await inter.response.send_message(embed=embed, ephemeral=True)

class SpooferView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SpooferSelect())

@bot.tree.command(name="spoofer", description="Lista i cennik spooferów")
@app_commands.checks.has_permissions(administrator=True)
async def spoofer(inter: discord.Interaction):
    desc = "``` 🛒 SPIDERMAFIA PRODUCTS × SPOOFER PRODUCTS ```\n\n**Products available from us:**\n• <:redengine:1561770287832244226> **Red Engine**\n• <:echo:1561770287832244225> **Echo.Fun**"
    embed = discord.Embed(description=desc, color=discord.Color.dark_embed())
    embed.set_image(url=PRICE_LIST_BANNER)
    await inter.response.send_message(embed=embed, view=SpooferView())


# --- 7. SKLEP: /vpn ---
class VPNSelect