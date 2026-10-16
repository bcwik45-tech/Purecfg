import os
import threading
from datetime import time, timezone, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- NATYCHMIASTOWY SERWER HTTP DLA RAILWAY ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()
# ---------------------------------------------

import discord
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.bans = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_CHANNEL_ID = 1556280506516115466
BOOST_CHANNEL_ID = 1540358387219304592
MINIGAME_CHANNEL_ID = 1556566161653764157
IMG_URL = "https://cdn.discordapp.com/attachments/1548988126452781137/1560367951020953651/coldcfg2.gif"
WINNER_ROLE_ID = 1556565240832073779
ACCEPT_ROLE_ID = 1540360249775493230

TICKET_CATEGORIES = {
    "shop": 1556300130892906506,
    "owner": 1556300080355606608,
    "support": 1556300180624769105,
    "recruitment": 1556300236526329936,
    "partner": 1556383124424892606
}

TICKET_EMOJIS = {
    "shop": "🛒",
    "owner": "👑",
    "support": "❓",
    "recruitment": "📄",
    "partner": "🤝"
}

TICKET_ROLES = {
    "shop": [1540359821323149392],
    "owner": [1540359821323149392, 1540495893399081061],
    "support": [1540359821323149392, 1540495893399081061, 1556062543963750400, 1540359905175801946, 1540360086617063584],
    "recruitment": [1540359821323149392, 1540495893399081061, 1556062543963750400, 1540359905175801946],
    "partner": [1540359821323149392, 1540495893399081061]
}

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zamknij ticket 🔒", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Zamykanie i usuwanie ticketu...", ephemeral=True)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"Błąd przy zamykaniu ticketu: {e}")

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Owner", description="Ticket with a matter for the config owners", emoji="👑", value="owner"),
            discord.SelectOption(label="Shop", description="Ticket for purchase an item from our store", emoji="🛒", value="shop"),
            discord.SelectOption(label="Support", description="Support ticket for help in our config server", emoji="❓", value="support"),
            discord.SelectOption(label="Recruitment", description="Application or recruitment matters", emoji="📄", value="recruitment"),
            discord.SelectOption(label="Partner", description="Ticket for partnership", emoji="🤝", value="partner")
        ]
        super().__init__(placeholder="Select category...", min_values=1, max_values=1, options=options, custom_id="persistent_ticket_select")

    async def callback(self, interaction: discord.Interaction):
        ticket_type = self.values[0]
        guild = interaction.guild
        category_id = TICKET_CATEGORIES.get(ticket_type)
        category = guild.get_channel(category_id) if category_id else None
        allowed_role_ids = TICKET_ROLES.get(ticket_type, [])
        emoji = TICKET_EMOJIS.get(ticket_type, "🎫")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        for r_id in allowed_role_ids:
            role = guild.get_role(r_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        channel_name = f"{emoji}-ticket-{ticket_type}-{interaction.user.name}".lower()
        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

        role_pings = " ".join([f"<@&{r_id}>" for r_id in allowed_role_ids])

        embed = discord.Embed(
            title=f"Ticket: {ticket_type.upper()}",
            description=f"Witaj <@!{interaction.user.id}>!\nAdministracja wkrótce odpowie na Twoje zgłoszenie.\n\nAby zamknąć ten kanał, kliknij przycisk poniżej.",
            color=0x2b2d31
        )
        embed.set_image(url=IMG_URL)
        await ticket_channel.send(content=f"{role_pings} <@!{interaction.user.id}>", embeds=[embed], view=CloseTicketView())
        await interaction.response.send_message(f"Utworzono Twój ticket: {ticket_channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.success, emoji="✅", custom_id="verify_btn_new")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ACCEPT_ROLE_ID)
        if not role:
            return await interaction.response.send_message("Nie znaleziono roli weryfikacji.", ephemeral=True)
        
        if role in interaction.user.roles:
            await interaction.response.send_message("Jesteś już zweryfikowany!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("Pomyślnie zweryfikowano!", ephemeral=True)

POLAND_TZ = timezone(timedelta(hours=1))
@tasks.loop(time=time(hour=18, minute=0, tzinfo=POLAND_TZ))
async def minigame_daily_reminder():
    if MINIGAME_CHANNEL_ID == 0:
        return
    channel = bot.get_channel(MINIGAME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="Daily reminder 🦦",
            description="Use /minigame to win an award! Booster gets something more!",
            color=0x2b2d31
        )
        embed.set_image(url=IMG_URL)
        await channel.send(content=f"<@&{ACCEPT_ROLE_ID}>", embed=embed)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}!")
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
    if not minigame_daily_reminder.is_running():
        minigame_daily_reminder.start()
    try:
        synced = await bot.tree.sync()
        print(f"Zsynchronizowano {len(synced)} komend slash.")
    except Exception as e:
        print(e)

@bot.event
async def on_member_join(member: discord.Member):
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return

    created_str = member.created_at.strftime("%d.%m.%Y %H:%M:%S")
    joined_str = member.joined_at.strftime("%d.%m.%Y %H:%M:%S") if member.joined_at else "N/A"

    desc = (
        f"🎉 Hi\n"
        f"<@!{member.id}>\n"
        f"Welcome to the best cfg in Poland!\n"
        f"Go check out our stuff!\n\n"
        f"**You're our {member.guild.member_count} member!**\n\n"
        f"**Member Info:**\n"
        f"🪪 **Discord account created:**\n"
        f"`{created_str}`\n"
        f"👤 **Username:** `{member.name}`\n"
        f"📅 **Joined at:** `{joined_str}`"
    )

    embed = discord.Embed(title="New member!", description=desc, color=0x2b2d31)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url=IMG_URL)
    await channel.send(embed=embed)

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.premium_since is None and after.premium_since is not None:
        channel = after.guild.get_channel(BOOST_CHANNEL_ID)
        if not channel:
            return

        embed = discord.Embed(
            title="💎 New server Boost!",
            description=(
                f"<@!{after.id}> BOOST!\n"
                f"> thanks for boosting our server!\n"
                f"> Go check out our booster zone!\n\n"
                f"**Boost Info:**\n"
                f"🧊 **Server Boost level:** `{after.guild.premium_tier}`\n"
                f"🔢 **Boost count:** `{after.guild.premium_subscription_count}`"
            ),
            color=0xff73fa
        )
        embed.set_thumbnail(url=after.display_avatar.url)
        embed.set_image(url=IMG_URL)
        embed.set_footer(text=after.guild.name)
        await channel.send(embed=embed)

@bot.tree.command(name="say", description="Send message as embed")
async def say(interaction: discord.Interaction, message: str):
    embed = discord.Embed(description=message, color=0x2b2d31)
    embed.set_image(url=IMG_URL)
    embed.set_footer(text=f"Bot • Ad made by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="bandc", description="Ban user permanently")
@discord.app_commands.checks.has_permissions(ban_members=True)
async def bandc(interaction: discord.Interaction, target: discord.User, reason: str):
    await interaction.guild.ban(target, reason=reason)
    embed = discord.Embed(title="🔨 User has been banned for life", color=0xff0000)
    embed.add_field(name="👤 User", value=f"<@!{target.id}>", inline=True)
    embed.add_field(name="🆔 ID", value=f"`{target.id}`", inline=True)
    embed.add_field(name="🛡️ Administrator", value=f"<@!{interaction.user.id}>", inline=False)
    embed.add_field(name="📝 Reason", value=reason, inline=False)
    embed.set_image(url=IMG_URL)
    embed.set_footer(text=f"{interaction.guild.name} Security")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="unbandc", description="Unban user from server")
@discord.app_commands.checks.has_permissions(ban_members=True)
async def unbandc(interaction: discord.Interaction, userid: str, reason: str = "Brak powodu"):
    user = await bot.fetch_user(int(userid))
    await interaction.guild.unban(user, reason=reason)
    embed = discord.Embed(title="User has been unbanned", color=0x00ff00)
    embed.add_field(name="User", value=f"<@!{userid}>", inline=True)
    embed.set_image(url=IMG_URL)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="minigame", description="Try your luck in Cold Cfg minigame")
@discord.app_commands.checks.cooldown(1, 86400)
async def minigame(interaction: discord.Interaction):
    import random
    won = random.choice([True] + [False] * 34)

    if won:
        role = interaction.guild.get_role(WINNER_ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
        
        embed = discord.Embed(
            title="🎉 Congratulations! You won!",
            description=(
                f"<@!{interaction.user.id}>, you successfully won in our minigame and received a special rank!\n\n"
                f"**Some Info:**\n"
                f"_Your chance was **1 in 35**._\n\n"
                f"Enjoy your reward!"
            ),
            color=0x2ecc71
        )
    else:
        embed = discord.Embed(
            title="🐱 We're sorry!",
            description=(
                f"<@!{interaction.user.id}>, this time you didn't win anything. Try your luck again tomorrow!\n\n"
                f"**Some Info:**\n"
                f"_Your chance was **1 in 35**._\n\n"
                f"We wish you better luck next time!"
            ),
            color=0x2b2d31
        )

    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_image(url=IMG_URL)
    await interaction.response.send_message(content=f"<@!{interaction.user.id}>", embed=embed)

@minigame.error
async def minigame_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CommandOnCooldown):
        hours = int(error.retry_after // 3600)
        minutes = int((error.retry_after % 3600) // 60)
        await interaction.response.send_message(
            f"Możesz zagrać ponownie dopiero za ok. {hours}h {minutes}m!",
            ephemeral=True
        )

@bot.tree.command(name="accept", description="Accept candidate and give roles")
async def accept(interaction: discord.Interaction, target: discord.Member):
    required_role = interaction.guild.get_role(ACCEPT_ROLE_ID)
    if not required_role or required_role not in interaction.user.roles:
        return await interaction.response.send_message("Nie masz uprawnień do użycia tej komendy.", ephemeral=True)

    role = interaction.guild.get_role(ACCEPT_ROLE_ID)
    if role:
        await target.add_roles(role)
    await interaction.response.send_message(f"Pomyślnie nadano rolę użytkownikowi <@!{target.id}>!", ephemeral=True)

@bot.tree.command(name="setup_weryfikacja", description="Send verification panel")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_weryfikacja(interaction: discord.Interaction):
    verify_embed = discord.Embed(
        title="Verification",
        description=(
            "Welcome to **COLDCFG**! 🧊\n\n"
            "To gain access to the rest of the server and unlock all channels, please verify your account by clicking the button below.\n\n"
            "> 🔒 **Security Check:** Automated protection is active.\n"
            "> ⚡ **Access:** Instant role assignment upon verification.\n\n"
            "Click the button below to verify yourself."
        ),
        color=0x2ecc71
    )
    verify_embed.set_image(url=IMG_URL)
    await interaction.channel.send(embed=verify_embed, view=VerifyView())
    await interaction.response.send_message("Wysłano nowy panel weryfikacji!", ephemeral=True)

@bot.tree.command(name="setup_tickets", description="Send tickets panel")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_tickets(interaction: discord.Interaction):
    ticket_embed = discord.Embed(
        title="Tickets",
        description=(
            "**Ticket Owner**\n*Open if you have a demand to the owners.*\n\n"
            "**Ticket Shop**\n*Open if you want to buy something.*\n\n"
            "**Ticket Support**\n*Open if you need any help.*\n\n"
            "**Ticket Partner**\n*Open if you want to collaborate with us.*\n\n"
            "For any issues, text us in #chat."
        ),
        color=0x2b2d31
    )
    ticket_embed.set_image(url=IMG_URL)
    await interaction.channel.send(embed=ticket_embed, view=TicketView())
    await interaction.response.send_message("Wysłano panel biletów z menu rozwijanym!", ephemeral=True)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))