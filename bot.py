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


# --- 1. WERYFIKACJA I POWITANIA (/setup_weryfikacja) ---
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

@bot.tree.command(name="setup_weryfikacja", description="Send verification panel")
@app_commands.checks.has_permissions(administrator=True)
async def setup_weryfikacja(inter: discord.Interaction):
    embed = discord.Embed(
        title="Weryfikacja Spidermafia",
        description="Kliknij przycisk poniżej, aby zweryfikować swoje konto.",
        color=discord.Color.from_rgb(180, 0, 0)
    )
    await inter.channel.send(embed=embed, view=VerifyView())
    await inter.response.send_message("Wysłano panel weryfikacji.", ephemeral=True)


# --- 2. TICKETY (/setup_tickets) ---
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

@bot.tree.command(name="setup_tickets", description="Send tickets panel")
@app_commands.checks.has_permissions(administrator=True)
async def setup_tickets(inter: discord.Interaction):
    embed = discord.Embed(title="Tickets", description="Wybierz kategorię ticketa z menu poniżej.", color=discord.Color.dark_embed())
    await inter.channel.send(embed=embed, view=TicketView())
    await inter.response.send_message("Wysłano panel ticketów.", ephemeral=True)


# --- 3. POZOSTAŁE KOMENDY (/globalinfo, /reviews, /accept, /say, /minigame, /bandc, /unbandc) ---
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

@bot.tree.command(name="accept", description="Accept candidate and give roles")
@app_commands.checks.has_permissions(administrator=True)
async def accept(inter: discord.Interaction, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await inter.response.send_message(f"Zaakceptowano kandydata {member.mention} i przyznano rolę {role.mention}.", ephemeral=True)

@bot.tree.command(name="say", description="Send message as embed")
@app_commands.checks.has_permissions(administrator=True)
async def say(inter: discord.Interaction, message: str):
    embed = discord.Embed(description=message, color=discord.Color.from_rgb(180, 0, 0))
    await inter.channel.send(embed=embed)
    await inter.response.send_message("Wysłano wiadomość embed.", ephemeral=True)

@bot.tree.command(name="minigame", description="Try your luck in Spidermafia minigame")
@app_commands.checks.has_permissions(administrator=True)
async def minigame(inter: discord.Interaction):
    await inter.response.send_message("🎲 Minigra Spidermafia: Wkrótce dostępne!", ephemeral=True)

@bot.tree.command(name="bandc", description="Ban user permanently")
@app_commands.checks.has_permissions(administrator=True)
async def bandc(inter: discord.Interaction, member: discord.Member, reason: str = "Brak powody"):
    await member.ban(reason=reason)
    await inter.response.send_message(f"Zbanowano {member.mention}. Powód: {reason}", ephemeral=True)

@bot.tree.command(name="unbandc", description="Unban user from server")
@app_commands.checks.has_permissions(administrator=True)
async def unbandc(inter: discord.Interaction, user_id: str):
    user = await bot.fetch_user(int(user_id))
    await inter.guild.unban(user)
    await inter.response.send_message(f"Odbanowano użytkownika {user.name}.", ephemeral=True)


# --- 4. SKLEP: /cheats, /spoofer, /vpn, /bundle, /counterstrike ---
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


class VPNSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="IPVANISH", description="Year — 10 PLN", emoji=discord.PartialEmoji.from_str("<:ipvanish:1561774215039025273>"))
        ]
        super().__init__(placeholder="❌ × Wybierz wariant...", min_values=1, max_values=1, options=options)

    async def callback(self, inter: discord.Interaction):
        val = self.values[0]
        if val == "IPVANISH":
            desc = "``` IPVANISH ```\n\n│ ***PRICE LIST*** 💸\n\n│ • 📅 **Year** » `10 PLN` 💸"
            embed = discord.Embed(description=desc, color=discord.Color.from_rgb(0, 180, 0))
            embed.set_image(url=VPN_BANNER)
            await inter.response.send_message(embed=embed, ephemeral=True)

class VPNView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(VPNSelect())

@bot.tree.command(name="vpn", description="Panel i cennik produktów VPN")
@app_commands.checks.has_permissions(administrator=True)
async def vpn(inter: discord.Interaction):
    desc = "``` 🛒 SPIDERMAFIA PRODUCTS × VPN PRODUCTS ```\n\n**Products available from us:**\n• <:ipvanish:1561774215039025273> **IPVANISH**"
    embed = discord.Embed(description=desc, color=discord.Color.dark_embed())
    embed.set_image(url=PRICE_LIST_BANNER)
    await inter.response.send_message(embed=embed, view=VPNView())


class BundleSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="STEAM", description="See price", emoji=discord.PartialEmoji.from_str("<:steam:1561775794626240563>")),
            discord.SelectOption(label="DISCORD", description="See price", emoji=discord.PartialEmoji.from_str("<:discord:1561776241780981810>")),
            discord.SelectOption(label="FIVEM READY", description="See price", emoji=discord.PartialEmoji.from_str("<:fivemready:1561778286516764682>"))
        ]
        super().__init__(placeholder="❌ × Wybierz ofertę z listy", min_values=1, max_values=1, options=options)

    async def callback(self, inter: discord.Interaction):
        val = self.values[0]
        if val == "STEAM":
            desc = "``` STE$M ```\n\n│ ***Ceny:*** 💸\n│ • <:steam:1561775794626240563> **x1** » `0.40 PLN` 💸\n\n│ ***Krótki Opis:***\n│ 🟢 » Full Access\n│ 🟢 » Gotowy do użycia\n│ 🟢 » Nie ma banów"
            embed = discord.Embed(description=desc, color=discord.Color.from_rgb(180, 0, 0))
            embed.set_image(url=STEAM_BANNER)
            await inter.response.send_message(embed=embed, ephemeral=True)
        elif val == "DISCORD":
            desc = "``` DISC$RD ```\n\n│ ***Ceny:*** 💸\n│ • <:discord:1561776241780981810> **Email + Phone Verified** » `1.00 PLN` 💸\n│ • <:discord:1561776241780981810> **Token Email + Phone Verified** » `0.70 PLN` 💸\n\n│ ***Krótki Opis:***\n│ 🟢 » Full Access\n│ 🟢 » Gotowy do użycia\n│ 🟢 » Nie ma banów"
            embed = discord.Embed(description=desc, color=discord.Color.from_rgb(180, 0, 0))
            embed.set_image(url=DISCORD_BANNER)
            await inter.response.send_message(embed=embed, ephemeral=True)
        elif val == "FIVEM READY":
            desc = "``` FIVEM READY ```\n\n│ ***Ceny:*** 💸\n│ • <:fivemready:1561778286516764682> **x1** » `0.70 PLN` 💸\n│ • <:fivemready:1561778286516764682> **x6** » `3.00 PLN` 💸\n\n│ ***Krótki Opis:***\n│ 🟢 » Full Access\n│ 🟢 » Gotowy do użycia\n│ 🟢 » Nie ma banów\n│ 🟢 » 100% Fresh"
            embed = discord.Embed(description=desc, color=discord.Color.from_rgb(180, 0, 0))
            await inter.response.send_message(embed=embed, ephemeral=True)

class BundleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(BundleSelect())

@bot.tree.command(name="bundle", description="Lista i cennik kont oraz bundle")
@app_commands.checks.has_permissions(administrator=True)
async def bundle(inter: discord.Interaction):
    desc = "``` 🛒 SPIDERMAFIA PRODUCTS × ACCOUNTS PRODUCTS ```\n\n**Products available from us:**\n• <:steam:1561775794626240563> **STEAM**\n• <:discord:1561776241780981810> **DISCORD**\n• <:fivemready:1561778286516764682> **FIVEM READY**"
    embed = discord.Embed(description=desc, color=discord.Color.dark_embed())
    embed.set_image(url=BUNDLE_MAIN_BANNER)
    await inter.response.send_message(embed=embed, view=BundleView())


class CounterStrikeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Memesense", description="See price", emoji=discord.PartialEmoji.from_str("<:memesense:1561768601948520639>")),
            discord.SelectOption(label="Prime Ready", description="See price", emoji=discord.PartialEmoji.from_str("<:cs_ready:1561784269846876363>")),
            discord.SelectOption(label="Premier Ready (4+ Medals)", description="See price", emoji=discord.PartialEmoji.from_str("<:cs_ready:1561784269846876363>"))
        ]
        super().__init__(placeholder="❌ × Wybierz ofertę z listy", min_values=1, max_values=1, options=options)

    async def callback(self, inter: discord.Interaction):
        val = self.values[0]
        if val == "Memesense":
            desc = "``` MEMESENSE ```\n\n│ ***PRICE LIST*** 💸\n\n│ • 📅 **14 Days** » `18 PLN` 💸\n│ • 📅 **31 Days** » `25 PLN` 💸\n│ • 📅 **90 Days** » `53 PLN` 💸\n│ • 📅 **180 Days** » `88 PLN` 💸"
            embed = discord.Embed(description=desc, color=discord.Color.from_rgb(180, 0, 0))
            embed.set_image(url=MEMESENSE_BANNER)
            await inter.response.send_message(embed=embed, ephemeral=True)
        elif val == "Prime Ready":
            desc = "``` PRIME READY ```\n\n│ ***PRICE LIST*** 💸\n\n│ • <:cs_ready:1561784269846876363> **Prime Ready** » `8 PLN` 💸\n\n│ ***Krótki Opis:***\n│ 🟢 » Full Access\n│ 🟢 » Gotowy do użycia\n│ 🟢 » Status Prime"
            embed = discord.Embed(description=desc, color=discord.Color.from_rgb(180, 0, 0))
            await inter.response.send_message(embed=embed, ephemeral=True)
        elif val == "Premier Ready (4+ Medals)":
            desc = "``` PREMIER READY (4+ MEDALS) ```\n\n│ ***PRICE LIST*** 💸\n\n│ • <:cs_ready:1561784269846876363> **Premier Ready** » `10 PLN` 💸\n\n│ ***Krótki Opis:***\n│ 🟢 » Full Access\n│ 🟢 » 4+ Medals\n│ 🟢 » Gotowy do Premier"
            embed = discord.Embed(description=desc, color=discord.Color.from_rgb(180, 0, 0))
            await inter.response.send_message(embed=embed, ephemeral=True)

class CounterStrikeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CounterStrikeSelect())

@bot.tree.command(name="counterstrike", description="Lista i cennik produktów Counter-Strike")
@app_commands.checks.has_permissions(administrator=True)
async def counterstrike(inter: discord.Interaction):
    desc = "``` 🛒 SPIDERMAFIA PRODUCTS × CS2 PRODUCTS ```\n\n**Products available from us:**\n• <:memesense:1561768601948520639> **Memesense**\n• <:cs_ready:1561784269846876363> **Prime Ready**\n• <:cs_ready:1561784269846876363> **Premier Ready (4+ Medals)**"
    embed = discord.Embed(description=desc, color=discord.Color.dark_embed())
    embed.set_image(url=CS_MAIN_BANNER)
    await inter.response.send_message(embed=embed, view=CounterStrikeView())


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot {bot.user} jest gotowy i zsynchronizowany!")

bot.run(os.getenv("DISCORD_TOKEN"))