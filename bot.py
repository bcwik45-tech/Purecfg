import os
import datetime
import random
from zoneinfo import ZoneInfo
import discord
from discord.ext import commands, tasks
from discord import app_commands

# --- KONFIGURACJA SAVAGE ---
EMBED_COLOR = 0x2B2D31
BANNER_URL = "https://cdn.discordapp.com/attachments/1563292364414648471/1563987942819762176/Gemini_Generated_Image_ksdzv8ksdzv8ksdz.jpg"
FOOTER_TEXT = "Savage"

# --- ID KANAŁÓW I RÓL ---
WELCOME_CHANNEL_ID = 1561740336726937660
BOOST_CHANNEL_ID = 1563296339847282771
TICKET_CHANNEL_ID = 1561742350986903702
MINIGAME_CHANNEL_ID = 1562815793547182173
ALLOWED_COMMAND_CHANNEL_ID = 1561758533446410251

AUTO_ROLE_ID = 1540360249775493230
MINIGAME_REWARD_ROLE_ID = 1562816846535729222

# Konfiguracja ról i kategorii ticketów
TICKET_CONFIGS = {
    "Owner": {
        "category_id": 1563539138073075795,
        "allowed_roles": [1540359821323149392, 1540495893399081061],
        "emoji": "👑",
        "desc": "ticket with a matter for the config owners"
    },
    "Partner": {
        "category_id": 1563539138073075795,
        "allowed_roles": [1556315623045333064, 1540359905175801946, 1556062543963750400, 1540495893399081061, 1540359821323149392],
        "emoji": "🤝",
        "desc": "Ticket for partnership"
    },
    "Recruitment": {
        "category_id": 1563539309120847963,
        "allowed_roles": [1540359821323149392, 1540495893399081061],
        "emoji": "📝",
        "desc": "Open if you want to join our team"
    }
}

minigame_cooldowns = {}

class SavageBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        print("Synchronizacja komend slash...")
        await self.tree.sync()
        print("Komendy slash zsynchronizowane!")
        daily_minigame_reminder.start()
        reset_minigame_cooldowns.start()

bot = SavageBot()

# --- ZDARZENIE: WEJŚCIE UŻYTKOWNIKA ---
@bot.event
async def on_member_join(member: discord.Member):
    role = member.guild.get_role(AUTO_ROLE_ID)
    if role:
        try:
            await member.add_roles(role)
        except Exception:
            pass

    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        member_count = member.guild.member_count
        embed = discord.Embed(
            title="SAVAGE × NOWA OSOBA",
            description=(
                f"↪ | Witaj {member.mention} na **SAVAGE**!\n"
                f"❤ | Mamy nadzieję, że zostaniesz z nami na dłużej\n\n"
                f"⚠ | Nieprzestrzeganie naszego **regulaminu** może wiązać się z karą\n\n"
                f"👤 | Jesteś naszym **{member_count}** użytkownikiem!"
            ),
            color=EMBED_COLOR
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        if BANNER_URL.startswith("http"):
            embed.set_image(url=BANNER_URL)
        embed.set_footer(text=FOOTER_TEXT)

        await channel.send(embed=embed)

# --- ZDARZENIE: SERWER BOOST ---
@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.premium_since is None and after.premium_since is not None:
        channel = after.guild.get_channel(BOOST_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="💎 New server Boost!",
                description=f"{after.mention} **BOOST!**\n> thanks for boosting our server!\n> *Go check out our booster zone!*",
                color=EMBED_COLOR
            )
            embed.add_field(
                name="Boost Info:",
                value=f"🪩 | **Server Boost level:** `{after.guild.premium_tier}`\n🔢 | **Boost count:** `{after.guild.premium_subscription_count}`",
                inline=False
            )
            embed.set_thumbnail(url=after.display_avatar.url)
            if BANNER_URL.startswith("http"):
                embed.set_image(url=BANNER_URL)
            embed.set_footer(text=FOOTER_TEXT)

            await channel.send(embed=embed)

# --- CODZIENNE PRZYPOMNIENIE O MINIGRZE (O 19:00) ---
@tasks.loop(time=datetime.time(hour=19, minute=0, tzinfo=ZoneInfo("Europe/Warsaw")))
async def daily_minigame_reminder():
    channel = bot.get_channel(MINIGAME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="🎮 Codzienna Minigra!",
            description="Czas spróbować swojego szczęścia w minigrze na naszym kanale! Wejdź i wygraj nagrody.",
            color=EMBED_COLOR
        )
        if BANNER_URL.startswith("http"):
            embed.set_image(url=BANNER_URL)
        embed.set_footer(text=FOOTER_TEXT)
        await channel.send(embed=embed)

# --- RESET COOLDOWNU O 23:59 ---
@tasks.loop(time=datetime.time(hour=23, minute=59, tzinfo=ZoneInfo("Europe/Warsaw")))
async def reset_minigame_cooldowns():
    minigame_cooldowns.clear()

@daily_minigame_reminder.before_loop
@reset_minigame_cooldowns.before_loop
async def before_loops():
    await bot.wait_until_ready()

# --- SYSTEM TICKETÓW Z PRZYCISKIEM ZAMYKANIA ---
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zamknij ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn", emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Zamykanie kanału za 3 sekundy...", ephemeral=True)
        import asyncio
        await asyncio.sleep(3)
        await interaction.channel.delete()

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Ticket Owner", description="ticket with a matter for the config owners", emoji="👑", value="Owner"),
            discord.SelectOption(label="Ticket Partner", description="Ticket for partnership", emoji="🤝", value="Partner"),
            discord.SelectOption(label="Ticket Recruitment", description="Open if you want to join our team", emoji="📝", value="Recruitment"),
        ]
        super().__init__(placeholder="Select category...", min_values=1, max_values=1, custom_id="ticket_select_cat", options=options)

    async def callback(self, interaction: discord.Interaction):
        key = self.values[0]
        cfg = TICKET_CONFIGS[key]
        guild = interaction.guild
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        for role_id in cfg["allowed_roles"]:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        category = guild.get_channel(cfg["category_id"])
        ticket_chan = await guild.create_text_channel(
            name=f"{key.lower()}-{interaction.user.name}", 
            category=category if isinstance(category, discord.CategoryChannel) else None,
            overwrites=overwrites
        )
        
        embed = discord.Embed(
            title=f"SAVAGE • {key}",
            description=f"Witaj {interaction.user.mention}!\nWybrano kategorię: **{key}**.\nOpisz swój problem lub sprawę.",
            color=EMBED_COLOR
        )
        if BANNER_URL.startswith("http"):
            embed.set_image(url=BANNER_URL)
        embed.set_footer(text=FOOTER_TEXT)
        
        await ticket_chan.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"✅ Utworzono ticket: {ticket_chan.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# --- KOMENDA SETUP TICKETS ---
@bot.tree.command(name="setup_tickets", description="Wysyła panel ticketów")
async def setup_tickets(interaction: discord.Interaction):
    if interaction.channel_id != ALLOWED_COMMAND_CHANNEL_ID:
        await interaction.response.send_message(f"❌ Tej komendy można używać tylko na kanale <#{ALLOWED_COMMAND_CHANNEL_ID}>!", ephemeral=True)
        return

    embed = discord.Embed(
        title="Tickets",
        description=(
            "👑 | **Ticket Owner**\n*Open if you have a demand to the owners*\n\n"
            "🤝 | **Ticket Partner**\n*Open if you want to collaborate with us*\n\n"
            "📝 | **Ticket Recruitment**\n*Open if you want to join our team*\n\n"
            "📌 | **For any issues, text on #chat**"
        ),
        color=EMBED_COLOR
    )
    if BANNER_URL.startswith("http"):
        embed.set_image(url=BANNER_URL)
    embed.set_footer(text=FOOTER_TEXT)
    
    channel = bot.get_channel(TICKET_CHANNEL_ID) or interaction.channel
    await channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("✅ Wysłano panel ticketów!", ephemeral=True)

# --- KOMENDA MINIGAME ---
@bot.tree.command(name="minigame", description="Zagraj w codzienną minigrę!")
async def minigame(interaction: discord.Interaction):
    if interaction.channel_id != MINIGAME_CHANNEL_ID:
        await interaction.response.send_message(f"❌ Minigry można używać tylko na kanale <#{MINIGAME_CHANNEL_ID}>!", ephemeral=True)
        return

    user_id = interaction.user.id
    dzis = datetime.datetime.now(ZoneInfo("Europe/Warsaw")).date()

    if minigame_cooldowns.get(user_id) == dzis:
        await interaction.response.send_message("⏳ Wykorzystałeś już próbę na dziś! Spróbuj ponownie jutro lub po godzinie 23:59.", ephemeral=True)
        return

    minigame_cooldowns[user_id] = dzis
    win = random.randint(1, 5) == 1

    embed = discord.Embed(color=EMBED_COLOR)
    if BANNER_URL.startswith("http"):
        embed.set_image(url=BANNER_URL)
    embed.set_footer(text=FOOTER_TEXT)

    if win:
        role = interaction.guild.get_role(MINIGAME_REWARD_ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
        embed.title = "🎉 Gratulacje!"
        embed.description = f"🐱 {interaction.user.mention}, **wygrałeś w minigrze!** Otrzymałeś specjalną nagrodę i rolę!"
    else:
        embed.title = "🐱 We're sorry!"
        embed.description = f"🐈 {interaction.user.mention}, **this time you didn't win anything.** Try your luck again tomorrow!\n\n**Some Info:**\n*Your chance was **1** in **5**.*\n\n*We wish you better luck next time!*"

    await interaction.response.send_message(embed=embed)

# --- KOMENDY BANDC / UNBANDC ---
@bot.tree.command(name="bandc", description="Banuje użytkownika na serwerze")
@app_commands.checks.has_permissions(ban_members=True)
async def bandc(interaction: discord.Interaction, member: discord.Member, reason: str = "Brak powodu"):
    await member.ban(reason=reason)
    
    embed = discord.Embed(
        title="🔨 User has been banned for life",
        color=0xFF0000
    )
    embed.add_field(name="👤 User", value=f"{member.mention}", inline=True)
    embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
    embed.add_field(name="🛡️ Administrator", value=f"{interaction.user.mention}", inline=False)
    embed.add_field(name="📝 Reason", value=f"`{reason}`", inline=False)
    if BANNER_URL.startswith("http"):
        embed.set_image(url=BANNER_URL)
    embed.set_footer(text="Savage Security")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="unbandc", description="Odbanowuje użytkownika po ID")
@app_commands.checks.has_permissions(ban_members=True)
async def unbandc(interaction: discord.Interaction, user_id: str):
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        
        embed = discord.Embed(
            title="🔓 User has been unbanned",
            description=f"Użytkownik **{user.name}** (`{user.id}`) został pomyślnie odbanowany.",
            color=0x00FF00
        )
        if BANNER_URL.startswith("http"):
            embed.set_image(url=BANNER_URL)
        embed.set_footer(text="Savage Security")
        
        await interaction.response.send_message(embed=embed)
    except Exception:
        await interaction.response.send_message("❌ Nie znaleziono użytkownika lub błąd odbanowania.", ephemeral=True)

# --- KOMENDA SAY W STYLU SAVAGE Z BANNEREM ---
@bot.tree.command(name="say", description="Wysyła ogłoszenie w stylu SAVAGE z bannerem na wskazany kanał")
@app_commands.checks.has_permissions(manage_messages=True)
async def say(
    interaction: discord.Interaction, 
    channel_id: str, 
    tytul: str, 
    wiadomosc: str
):
    if interaction.channel_id != ALLOWED_COMMAND_CHANNEL_ID:
        await interaction.response.send_message(f"❌ Tej komendy można używać tylko na kanale <#{ALLOWED_COMMAND_CHANNEL_ID}>!", ephemeral=True)
        return

    try:
        channel = bot.get_channel(int(channel_id))
        if not channel:
            await interaction.response.send_message("❌ Nie znaleziono kanału o podanym ID.", ephemeral=True)
            return

        formatted_message = wiadomosc.replace("\\n", "\n")

        embed = discord.Embed(
            title=f"SAVAGE × {tytul}",
            description=formatted_message,
            color=EMBED_COLOR
        )

        if BANNER_URL.startswith("http"):
            embed.set_image(url=BANNER_URL)
            
        embed.set_footer(text=FOOTER_TEXT)

        await channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Wysłano ogłoszenie na kanał {channel.mention}!", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"❌ Wystąpił błąd: {e}", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user.name}!")
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())

token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("BŁĄD: Brak zmiennej DISCORD_TOKEN!")