import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord.ext import commands
from discord import app_commands

# --- SERWER HTTP DLA RENDERA ---
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

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- KONFIGURACJA ID I LINKÓW ---
BANNER_URL = "https://cdn.discordapp.com/attachments/1563303323539476520/1563889238045626438/bannercvg.jpg?ex=6adf44da&is=6addf35a&hm=3d9fa13ed9b59f3341beef572ff7113b50f0ba1024eeb0e5643c98b17bc9153a&"

# Kanały
SETUP_CMD_CHANNEL_ID = 1561758533446410251
TICKET_PANEL_CHANNEL_ID = 1561742350986903702
WELCOME_CHANNEL_ID = 1561740336726937660
BOOST_CHANNEL_ID = 1563296339847282771
FAQ_CHANNEL_ID = 1561758533446410251 # Kanał na którym stawiamy panel FAQ (lub podaj inny)
TRACKED_CHANNEL_ID = 1563295322669711471 # Kanał śledzony w FAQ

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
            ),
        ]
        super().__init__(placeholder="➔ Select category...", min_values=1, max_values=1, options=options, custom_id="ticket_select_menu")

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

# --- GLOBAL INFO / FAQ SELECT MENU ---
class GlobalInfoSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Regulamin | Statute",
                description="Przeczytaj zasady panujące na serwerze. | Read rules.",
                emoji="📄",
                value="rules"
            ),
            discord.SelectOption(
                label="FAQ",
                description="Najczęściej zadawane pytania. | Frequently asked questions.",
                emoji="❓",
                value="faq"
            ),
            discord.SelectOption(
                label="Information Partnership",
                description="Information Partnership rules.",
                emoji="🤝",
                value="partnership"
            ),
        ]
        super().__init__(placeholder="! | Select the section that interests you", min_values=1, max_values=1, options=options, custom_id="global_info_select")

    async def callback(self, interaction: discord.Interaction):
        val = self.values[0]

        if val == "rules":
            view = RulesLangView()
            embed = discord.Embed(
                title="📄 ｜ REGULAMIN SERWERA",
                description="Nieznajomość regulaminu nie zwalnia Cię z jego przestrzegania. Dołączając na serwer, akceptujesz wszystkie poniższe zasady.\n\n**Regulamin Ogólny:**\n1. Nie tolerujemy wyzwisk, leaków ani innych działań uprzykrzających życie osobom na naszym lub innych serwerach. Publikowanie takich informacji skutkuje BANEM.\n2. Głupie pytania połączone z ciągłym oznaczaniem (pingu) administracji skutkować będą przerwą/mutem.\n3. Należy przestrzegać regulaminu Discord TOS.\n4. Publikowanie podejrzanych linków na kanałach pisemnych będzie karana BANEM.",
                color=0x2b2d31
            )
            embed.set_image(url=BANNER_URL)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif val == "faq":
            ticket_chan = discord.utils.get(interaction.guild.text_channels, name="ticket") or discord.utils.get(interaction.guild.text_channels, name="🛒・ticket")
            ticket_mention = ticket_chan.mention if ticket_chan else "#🛒・ticket"
            tracked_chan = interaction.guild.get_channel(TRACKED_CHANNEL_ID)
            tracked_mention = tracked_chan.mention if tracked_chan else f"<#{TRACKED_CHANNEL_ID}>"

            embed = discord.Embed(
                title="❓