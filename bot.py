import os
import datetime
from zoneinfo import ZoneInfo
import discord
from discord.ext import commands, tasks
from discord import app_commands

# --- KONFIGURACJA POLISHCFG ---
EMBED_COLOR = 0x2B2D31
BANNER_URL = "https://cdn.discordapp.com/attachments/1556074439030865950/1562881661358706870/gg.polishcfg.png"
FOOTER_TEXT = "POLISHCFG • Wszelkie prawa zastrzeżone"

# --- ID KANAŁÓW I RÓL ---
WELCOME_CHANNEL_ID = 1561740336726937660
BOOST_CHANNEL_ID = 1561740466989301821      # Kanał dla boostów
TICKET_CHANNEL_ID = 1561742350986903702
MINIGAME_CHANNEL_ID = 1562815793547182173
ALLOWED_COMMAND_CHANNEL_ID = 1561758533446410251

AUTO_ROLE_ID = 1540360249775493230
MINIGAME_REWARD_ROLE_ID = 1562816846535729222

minigame_cooldowns = {}

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
        daily_minigame_reminder.start()
        reset_minigame_cooldowns.start()

bot = PolishBot()

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
        created_at = member.created_at.strftime("%Y-%m-%d %H:%M:%S")
        joined_at = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")

        embed = discord.Embed(
            title="New user joined us! 🙂",
            description=f"👋 **Hi {member.mention} We're glad to have you here!**\n\nGo check out our fivem stuff!\nDon't forget to read the rules!\n**You're our {member_count} member!**",
            color=EMBED_COLOR
        )
        embed.add_field(
            name="📢 User Information",
            value=f"👾 **Discord account created:** `<t:{int(member.created_at.timestamp())}:R>` ({created_at})\n👤 **Username:** `{member.name}`\n📅 **Joined at:** `{joined_at}`",
            inline=False
        )
        if BANNER_URL.startswith("http"):
            embed.set_image(url=BANNER_URL)
        embed.set_footer(text="polishcfg")

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
                name="🚀 Boost level",
                value=f"🎲 **Server Boost level:** `{after.guild.premium_tier}`\n🔢 **Boost count:** `{after.guild.premium_subscription_count}`",
                inline=False
            )
            embed.set_thumbnail(url=after.display_avatar.url)
            if BANNER_URL.startswith("http"):
                embed.set_image(url=BANNER_URL)
            embed.set_footer(text="polishcfg")

            await channel.send(embed=embed)

# --- CODZIENNE PRZYPOMNIENIE O 19:00 ---
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

# --- PANEL TICKETÓW ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Owner", description="ticket with a matter for the config owners", emoji="👑"),
            discord.SelectOption(label="Shop", description="Ticket for purchase an item from our store", emoji="🛒"),
            discord.SelectOption(label="Support", description="Support ticket for help in our config server", emoji="❓"),
            discord.SelectOption(label="Partner", description="Ticket for partnership", emoji="🤝"),
        ]
        super().__init__(placeholder="Select category...", min_values=1, max_values=1, custom_id="ticket_select_cat", options=options)

    async def callback(self, interaction: discord.Interaction):
        cat = self.values[0]
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ticket_chan = await guild.create_text_channel(name=f"{cat.lower()}-{interaction.user.name}", overwrites=overwrites)
        
        embed = discord.Embed(
            title=f"POLISHCFG • {cat}",
            description=f"Witaj {interaction.user.mention}!\nWybrano kategorię: **{cat}**.\nOpisz swój problem lub sprawę.",
            color=EMBED_COLOR
        )
        if BANNER_URL.startswith("http"):
            embed.set_image(url=BANNER_URL)
        embed.set_footer(text=FOOTER_TEXT)
        
        await ticket_chan.send(embed=embed)
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
            "**Ticket Owner**\n*Open if you have a demand to the owners.*\n\n"
            "**Ticket Shop**\n*open if you you want to buy something.*\n\n"
            "**Ticket Support**\n*Open if you need any help.*\n\n"
            "**Ticket Partner**\n*Open if you want to collaborate with us.*\n\n"
            "**For any issues, text on #chat**"
        ),
        color=EMBED_COLOR
    )
    if BANNER_URL.startswith("http"):
        embed.set_image(url=BANNER_URL)
    embed.set_footer(text="POLISHCFG")
    
    channel = bot.get_channel(TICKET_CHANNEL_ID) or interaction.channel
    await channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("✅ Wysłano panel ticketów!", ephemeral=True)

# --- KOMENDA TESTOWA BOOST ---
@bot.tree.command(name="test_boost", description="Testuje wygląd powiadomienia o booscie")
async def test_boost(interaction: discord.Interaction):
    embed = discord.Embed(
        title="💎 New server Boost!",
        description=f"{interaction.user.mention} **BOOST!**\n> thanks for boosting our server!\n> *Go check out our booster zone!*",
        color=EMBED_COLOR
    )
    embed.add_field(
        name="🚀 Boost level",
        value=f"🎲 **Server Boost level:** `{interaction.guild.premium_tier}`\n🔢 **Boost count:** `{interaction.guild.premium_subscription_count}`",
        inline=False
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    if BANNER_URL.startswith("http"):
        embed.set_image(url=BANNER_URL)
    embed.set_footer(text="polishcfg")

    await interaction.response.send_message(embed=embed)

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
    
    import random
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
    embed.set_footer(text="POLISHCFG Security")

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
        embed.set_footer(text="POLISHCFG Security")
        
        await interaction.response.send_message(embed=embed)
    except Exception:
        await interaction.response.send_message("❌ Nie znaleziono użytkownika lub błąd odbanowania.", ephemeral=True)

# --- KOMENDA SAY ---
@bot.tree.command(name="say", description="Wysyła ramkę z wiadomością na wskazany kanał")
@app_commands.checks.has_permissions(manage_messages=True)
async def say(
    interaction: discord.Interaction, 
    channel_id: str, 
    wiadomosc: str, 
    tytul: str = None, 
    obrazek: str = None, 
    stopka: str = "polishcfg"
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
            title=tytul,
            description=formatted_message,
            color=EMBED_COLOR
        )

        if obrazek and obrazek.startswith("http"):
            embed.set_image(url=obrazek)

        if stopka:
            embed.set_footer(text=stopka)

        await channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Wysłano ramkę na kanał {channel.mention}!", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"❌ Wystąpił błąd: {e}", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user.name}!")
    bot.add_view(TicketView())

token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("BŁĄD: Brak zmiennej DISCORD_TOKEN!")