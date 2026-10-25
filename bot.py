import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord.ext import commands
from discord import app_commands

# --- SERWER HTTP DLA RENDERA (24/7 UPTIMEROBOT) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"OK")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        
    def log_message(self, format, *args):
        return # Wycisza spam logów HTTP

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Uruchomiono serwer HTTP na porcie {port}")
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- KONFIGURACJA ID I LINKÓW ---
BANNER_URL = "https://cdn.discordapp.com/attachments/1563292364414648471/1563987942819762176/Gemini_Generated_Image_ksdzv8ksdzv8ksdz.jpg?ex=6adfa0c7&is=6ade4f47&hm=52883c137fcd791f1631549995304d8b0c97184ebe5e50e089fb282ed35e174b&"

# Kanały
SETUP_CMD_CHANNEL_ID = 1561758533446410251
TICKET_PANEL_CHANNEL_ID = 1561742350986903702
WELCOME_CHANNEL_ID = 1561740336726937660
BOOST_CHANNEL_ID = 1563296339847282771
TRACKED_CHANNEL_ID = 1563295322669711471

# ID KATEGORII TICKETÓW
CATEGORY_OWNER_ID = 1563539435507683509
CATEGORY_RECRUITMENT_ID = 1563539309120847963
CATEGORY_PARTNER_ID = 1563539138073075795

# Rola startowa dla nowych osób
AUTO_ROLE_ID = 1540360249775493230

# Role z uprawnieniami do komend
ALLOWED_COMMAND_ROLES = [1540359821323149392, 1540495893399081061]

# Role w ticketach
OWNER_ROLES = [1540359821323149392, 1540495893399081061]
PARTNER_ROLES = [1540359821323149392, 1540495893399081061]
RECRUITMENT_ROLES = [1540359905175801946]

# --- SETUP BOTA ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def has_allowed_role(user: discord.Member) -> bool:
    user_role_ids = [role.id for role in user.roles]
    return any(role_id in ALLOWED_COMMAND_ROLES for role_id in user_role_ids)

# --- PRZYCISK ZAMYKANIA TICKETA ---
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zamknij ticket ❌", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="SAVAGE × TICKET",
            description="Ticket zostanie usunięty za kilka sekund...",
            color=0x2b2d31
        )
        embed.set_image(url=BANNER_URL)
        await interaction.response.send_message(embed=embed)
        await interaction.channel.delete()

# --- SELECT MENU DO TICKETA ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Ticket Owner",
                description="Open if you have a demand to the owners",
                emoji="👑",
                value="owner"
            ),
            discord.SelectOption(
                label="Ticket Partner",
                description="Open if you want to collaborate with us.",
                emoji="🤝",
                value="partner"
            ),
            discord.SelectOption(
                label="Ticket Recruitment",
                description="Open if you want to join our team",
                emoji="📝",
                value="recruitment"
            )
        ]
        super().__init__(placeholder="Select category...", min_values=1, max_values=1, options=options, custom_id="ticket_select_menu")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        category_name = self.values[0]
        
        ping_roles = []
        emoji_prefix = "🎫"
        target_category_id = None

        if category_name == "owner":
            ping_roles = OWNER_ROLES
            emoji_prefix = "👑"
            target_category_id = CATEGORY_OWNER_ID
        elif category_name == "partner":
            ping_roles = PARTNER_ROLES
            emoji_prefix = "🤝"
            target_category_id = CATEGORY_PARTNER_ID
        elif category_name == "recruitment":
            ping_roles = RECRUITMENT_ROLES
            emoji_prefix = "📝"
            target_category_id = CATEGORY_RECRUITMENT_ID

        category = guild.get_channel(target_category_id) if target_category_id else None
        channel_name = f"{emoji_prefix}・ticket-{interaction.user.name}"
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        for r_id in ping_roles:
            role = guild.get_role(r_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(
            name=channel_name, 
            category=category, 
            overwrites=overwrites
        )

        pings_formatted = " ".join([f"<@&{r_id}>" for r_id in ping_roles])
        
        embed = discord.Embed(
            title=f"SAVAGE × {category_name.upper()}",
            description="Cześć! Witaj w SAVAGE, opisz dokładnie swoją sytuację, a nasza administracja wkrótce Ci pomoże.",
            color=0x2b2d31
        )
        embed.set_image(url=BANNER_URL)

        await ticket_channel.send(content=f"{interaction.user.mention} {pings_formatted}", embed=embed, view=CloseTicketView())
        await interaction.followup.send(f"Stworzono ticket: {ticket_channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# --- EVENTY BOTA ---
@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
    try:
        synced = await bot.tree.sync()
        print(f"Zsynchronizowano {len(synced)} komend slash")
    except Exception as e:
        print(f"Błąd synchronizacji: {e}")

@bot.event
async def on_member_join(member: discord.Member):
    role = member.guild.get_role(AUTO_ROLE_ID)
    if role:
        try:
            await member.add_roles(role)
        except Exception as e:
            print(f"Błąd przy nadawania roli: {e}")

    welcome_channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if welcome_channel:
        embed = discord.Embed(
            title="SAVAGE × NOWA OSOBA",
            description=f"➥ | Witaj {member.mention} na **SAVAGE**!\n❤ | Mamy nadzieję, że zostaniesz z nami na dłużej\n\n⚠ | Nieprzestrzeganie naszego **regulaminu** może wiązać się z karą",
            color=0x2b2d31
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="", value=f"👤 | Jesteś naszym **{member.guild.member_count}** użytkownikiem!", inline=False)
        embed.set_image(url=BANNER_URL)
        await welcome_channel.send(embed=embed)

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if len(before.roles) < len(after.roles):
        premium_role = after.guild.premium_subscriber_role
        if premium_role and premium_role not in before.roles and premium_role in after.roles:
            boost_channel = after.guild.get_channel(BOOST_CHANNEL_ID)
            if boost_channel:
                embed = discord.Embed(
                    title="💎 New server Boost!",
                    description=f"{after.mention} **BOOST!**\nthanks for boosting our server!\nGo check out our booster zone!",
                    color=0x2b2d31
                )
                embed.set_thumbnail(url=after.display_avatar.url)
                embed.add_field(name="Boost Info:", value=f"🧊 **Server Boost level:** {after.guild.premium_tier}\n🔢 **Boost count:** {after.guild.premium_subscription_count}", inline=False)
                embed.set_image(url=BANNER_URL)
                await boost_channel.send(embed=embed)

# --- KOMENDY SLASH ---

@bot.tree.command(name="setup_tickets", description="Wysyła panel ticketów na odpowiedni kanał")
async def setup_tickets(interaction: discord.Interaction):
    if not has_allowed_role(interaction.user):
        return await interaction.response.send_message("Nie masz uprawnień do używania tej komendy!", ephemeral=True)

    if interaction.channel_id != SETUP_CMD_CHANNEL_ID:
        return await interaction.response.send_message(f"Tą komendę możesz wykonać tylko na kanale <#{SETUP_CMD_CHANNEL_ID}>!", ephemeral=True)

    target_channel = interaction.guild.get_channel(TICKET_PANEL_CHANNEL_ID)
    if not target_channel:
        return await interaction.response.send_message("Nie znaleziono docelowego kanału ticketów!", ephemeral=True)

    chat_channel = discord.utils.get(interaction.guild.text_channels, name="chat")
    chat_mention = chat_channel.mention if chat_channel else "#chat"

    embed = discord.Embed(
        title="Tickets",
        description=(
            "👑 | **Ticket Owner**\n"
            "Open if you have a demand to the owners\n\n"
            "🤝 | **Ticket Partner**\n"
            "Open if you want to collaborate with us\n\n"
            "📝 | **Ticket Recruitment**\n"
            "Open if you want to join our team\n\n"
            f"📌 | **For any issues, text on** {chat_mention}"
        ),
        color=0x2b2d31
    )
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text="Savage")
    
    await target_channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message(f"Pomyślnie wysłano panel ticketów na kanał {target_channel.mention}!", ephemeral=True)

@bot.tree.command(name="say", description="Wysyła ogłoszenie w formie estetycznego embeda")
@app_commands.describe(wiadomosc="Treść wiadomości", kanal="Kanał na którym ma zostać wysłana wiadomo