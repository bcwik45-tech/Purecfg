import discord
from discord.ext import commands
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- Serwer HTTP w tle utrzymujący status Online na Railway ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is online and running!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()
# -------------------------------------------------------------

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.bans = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_CHANNEL_ID = 1556280506516115466
BOOST_CHANNEL_ID = 1540358387219304592
IMG_URL = "https://i.imgur.com/rgprszrgprsz.png"

WINNER_ROLE_ID = 1556565240832073779

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

ACCEPT_ROLES = [1540359963346608168, 1540360086617063584]


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zamknij ticket 🔒", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Zamykanie ticketu za 3 sekundy...", ephemeral=True)
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=3))
        try:
            await interaction.channel.delete()
        except Exception:
            pass


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
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
        await ticket_channel.send(content=f"{role_pings} <@!{interaction.user.id}>", embeds=[embed], view=CloseTicketView())
        await interaction.response.send_message(f"Utworzono Twój ticket: {ticket_channel.mention}", ephemeral=True)

    @discord.ui.button(label="Shop 🛒", style=discord.ButtonStyle.success, custom_id="ticket_shop")
    async def shop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "shop")

    @discord.ui.button(label="Owner 👑", style=discord.ButtonStyle.secondary, custom_id="ticket_owner")
    async def owner_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "owner")

    @discord.ui.button(label="Support ❓", style=discord.ButtonStyle.primary, custom_id="ticket_support")
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "support")

    @discord.ui.button(label="Recruitment 📄", style=discord.ButtonStyle.danger, custom_id="ticket_recruitment")
    async def recruitment_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "recruitment")

    @discord.ui.button(label="Partnership 🤝", style=discord.ButtonStyle.secondary, custom_id="ticket_partner")
    async def partner_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "partner")


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj", style=discord.ButtonStyle.success, custom_id="verify_btn")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_id = ACCEPT_ROLES[0]
        role = interaction.guild.get_role(role_id)
        if not role:
            return await interaction.response.send_message("Nie znaleziono roli weryfikacji.", ephemeral=True)
        
        if role in interaction.user.roles:
            await interaction.response.send_message("Jesteś już zweryfikowany!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("Pomyślnie zweryfikowano!", ephemeral=True)


@bot.event
async def on_ready():
    print("Zalogowano pomyślnie!")
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
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

    desc = f"🎉 Hi\n<@!{member.id}>\nWelcome to the best cfg in Poland!\nGo check out our stuff!\n\n**You're our {member.guild.member_count} member!**\n\n**Username:** `{member.name}`"

    embed = discord.Embed(
        title="New member!",
        description=desc,
        color=0x2b2d31
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    await channel.send(embed=embed)


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.premium_since is None and after.premium_since is not None:
        channel = after.guild.get_channel(BOOST_CHANNEL_ID)
        if not channel:
            return

        embed = discord.Embed(
            title="New server Boost!",
            description=f"<@!{after.id}> BOOST!\n> thanks for boosting our server!\n> Go check out our booster zone!",
            color=0xff73fa
        )
        embed.set_thumbnail(url=after.display_avatar.url)
        embed.set_image(url=IMG_URL)
        await channel.send(embed=embed)


@bot.tree.command(name="say", description="Send message as embed")
async def say(interaction: discord.Interaction, message: str):
    embed = discord.Embed(description=message, color=0x2b2d31)
    embed.set_footer(text=f"Bot • Ad made by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="bandc", description="Ban user permanently")
@discord.app_commands.checks.has_permissions(ban_members=True)
async def bandc(interaction: discord.Interaction, target: discord.User, reason: str):
    await interaction.guild.ban(target, reason=reason)
    embed = discord.Embed(title="User has been banned for life", color=0xff0000)
    embed.add_field(name="User", value=f"<@!{target.id}>", inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_image(url=IMG_URL)
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
    won = random.choice([True] + [False] * 9)

    if won:
        role = interaction.guild.get_role(WINNER_ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
        
        embed = discord.Embed(
            title="Gratulacje! Wygrana!",
            description="Udało Ci się wygrać w minigrze i otrzymujesz specjalną rangę!",
            color=0x2ecc71
        )
    else:
        embed = discord.Embed(
            title="We are sorry!",
            description="This time you didn't win anything. Try your luck again tomorrow!",
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
@discord.app_commands.checks.has_permissions(manage_roles=True)
async def accept(interaction: discord.Interaction, target: discord.Member):
    for r_id in ACCEPT_ROLES:
        role = interaction.guild.get_role(r_id)
        if role:
            await target.add_roles(role)
    await interaction.response.send_message(f"Pomyślnie nadano rolę użytkownikowi <@!{target.id}>!", ephemeral=True)


@bot.tree.command(name="setup_weryfikacja", description="Send verification panel")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_weryfikacja(interaction: discord.Interaction):
    verify_embed = discord.Embed(title="Verification", description="Click on verification to get access", color=0x2ecc71)
    await interaction.channel.send(embed=verify_embed, view=VerifyView())
    await interaction.response.send_message("Wysłano panel weryfikacji!", ephemeral=True)


@bot.tree.command(name="setup_tickets", description="Send tickets panel")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_tickets(interaction: discord.Interaction):
    ticket_embed = discord.Embed(title="Tickets", description="Click a button to open a ticket.", color=0x3498db)
    await interaction.channel.send(embed=ticket_embed, view=TicketView())
    await interaction.response.send_message("Wysłano panel biletów!", ephemeral=True)


bot.run(os.getenv("DISCORD_TOKEN"))