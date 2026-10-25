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
BANNER_URL = "https://cdn.discordapp.com/attachments/1563303323539476520/1563889238045626438/bannercvg.jpg?ex=6adf44da&is=6addf35a&hm=3d9fa13ed9b59f3341beef572ff7113b50f0ba1024eeb0e5643c98b17bc9153a&"

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
            )
        ]
        super().__init__(placeholder="! | Select the section that interests you", min_values=1, max_values=1, options=options, custom_id="global_info_select")

    async def callback(self, interaction: discord.Interaction):
        val = self.values[0]

        if val == "rules":
            view = RulesLangView()
            embed = discord.Embed(
                title="📄 ｜ REGULAMIN SERWERA",
                description="""Nieznajomość regulaminu nie zwalnia Cię z jego przestrzegania. Dołączając na serwer, akceptujesz wszystkie poniższe zasady.

**Regulamin Ogólny:**
1. Nie tolerujemy wyzwisk, leaków ani innych działań uprzykrzających życie osobom na naszym lub innych serwerach. Publikowanie takich informacji skutkuje BANEM.
2. Głupie pytania połączone z ciągłym oznaczaniem (pingu) administracji skutkować będą przerwą/mutem.
3. Należy przestrzegać regulaminu Discord TOS.
4. Publikowanie podejrzanych linków na kanałach pisemnych będzie karana BANEM.""",
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
                title="❓ ｜ FAQ",
                description=(
                    f"• **Gdzie mogę zakupić coś z waszego sklepu?**\n"
                    f"• **Tickety** - {ticket_mention}\n\n"
                    f"• **Gdzie znajde tickety związane z supportem?**\n"
                    f"• znajdziesz je na kanale {ticket_mention}\n\n"
                    f"• **Jak dostać się do administracji?**\n"
                    f"• obserwuj kanał {tracked_mention}\n\n"
                    f"• **Czy transakcje są w pełni anonimowe?**\n"
                    f"• Tak! Wgląd do ticketów mają tylko osoby z rangą OWNER, co zapewnia wam 100% ochrony danych."
                ),
                color=0x2b2d31
            )
            embed.set_image(url=BANNER_URL)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif val == "partnership":
            view = PartnershipLangView()
            embed = discord.Embed(
                title="🤝 ｜ Jak nawiązać z nami partnerstwo?",
                description="• Wystarczy posiadać discorda na którym jest minimalnie 1000 osób.\n\n• Otwórz ticket i na pewno się dogadamy. Nie nawiązujemy partnerstw ze sklepami.",
                color=0x2b2d31
            )
            embed.set_image(url=BANNER_URL)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class GlobalInfoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GlobalInfoSelect())

# --- PRZYCISKI JĘZYKOWE ---
class RulesLangView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.is_polish = True

    @discord.ui.button(label="English 🇬🇧", style=discord.ButtonStyle.secondary, custom_id="toggle_rules_lang")
    async def toggle_lang(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.is_polish = not self.is_polish
        embed = discord.Embed(color=0x2b2d31)
        embed.set_image(url=BANNER_URL)

        if self.is_polish:
            button.label = "English 🇬🇧"
            embed.title = "📄 ｜ REGULAMIN SERWERA"
            embed.description = """Nieznajomość regulaminu nie zwalnia Cię z jego przestrzegania. Dołączając na serwer, akceptujesz wszystkie poniższe zasady.

**Regulamin Ogólny:**
1. Nie tolerujemy wyzwisk, leaków ani innych działań uprzykrzających życie osobom na naszym lub innych serwerach. Publikowanie takich informacji skutkuje BANEM.
2. Głupie pytania połączone z ciągłym oznaczaniem (pingu) administracji skutkować będą przerwą/mutem.
3. Należy przestrzegać regulaminu Discord TOS.
4. Publikowanie podejrzanych linków na kanałach pisemnych będzie karana BANEM."""
        else:
            button.label = "Polski 🇵🇱"
            embed.title = "📄 ｜ SERVER RULES (EN)"
            embed.description = """Ignorance of the rules does not exempt you from following them. By joining the server, you accept the following terms.

**General Rules:**
1. We do not tolerate insults, leaks, or any behavior that makes life difficult for people on our or other Discord servers. Posting such information results in a BAN.
2. Stupid questions combined with constant pinging will result in a timeout/mute.
3. You must abide by the Discord TOS.
4. Posting suspicious links in text channels will result in a BAN."""

        await interaction.response.edit_message(embed=embed, view=self)

class PartnershipLangView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.is_polish = True

    @discord.ui.button(label="English 🇬🇧", style=discord.ButtonStyle.secondary, custom_id="toggle_part_lang")
    async def toggle_lang(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.is_polish = not self.is_polish
        embed = discord.Embed(color=0x2b2d31)
        embed.set_image(url=BANNER_URL)

        if self.is_polish:
            button.label = "English 🇬🇧"
            embed.title = "🤝 ｜ Jak nawiązać z nami partnerstwo?"
            embed.description = "• Wystarczy posiadać discorda na którym jest minimalnie 1000 osób.\n\n• Otwórz ticket i na pewno się dogadamy. Nie nawiązujemy partnerstw ze sklepami."
        else:
            button.label = "Polski 🇵🇱"
            embed.title = "🤝 ｜ How to partner with us?"
            embed.description = "• You just need to have a Discord server with at least 1,000 members.\n\n• Open a ticket and we will definitely work something out. We do not partner with shops."

        await interaction.response.edit_message(embed=embed, view=self)

# --- EVENTY BOTA ---
@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
    bot.add_view(GlobalInfoView())
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
            "│ 👑 **Ticket Owner**\n"
            "*Open if you have a demand to the owners*\n\n"
            "│ 🤝 **Ticket Partner**\n"
            "*Open if you want to collaborate with us.*\n\n"
            "│ 📝 **Ticket Recruitment**\n"
            "*Open if you want to join our team*\n\n"
            f"│ **For any issues, text on** {chat_mention}"
        ),
        color=0x2b2d31
    )
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text="Savage")
    
    await target_channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message(f"Pomyślnie wysłano panel ticketów na kanał {target_channel.mention}!", ephemeral=True)

@bot.tree.command(name="faq", description="Wysyła panel SAVAGE x FAQ / GLOBAL INFO")
async def faq(interaction: discord.Interaction):
    if not has_allowed_role(interaction.user):
        return await interaction.response.send_message("Nie masz uprawnień do używania tej komendy!", ephemeral=True)

    embed = discord.Embed(
        title="SAVAGE x FAQ",
        description=(
            "│ • Wybierz interesującą Cię sekcję z menu poniżej.\n"
            "│ • Select the section you are interested in from the menu below."
        ),
        color=0x2b2d31
    )
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text="Savage™ • GLOBAL INFO")

    await interaction.channel.send(embed=embed, view=GlobalInfoView())
    await interaction.response.send_message("Pomyślnie wysłano panel FAQ!", ephemeral=True)

@bot.tree.command(name="say", description="Wysyła ogłoszenie w formie estetycznego embeda")
@app_commands.describe(wiadomosc="Treść wiadomości", kanal="Kanał na którym ma zostać wysłana wiadomość")
async def say(interaction: discord.Interaction, wiadomosc: str, kanal: discord.TextChannel):
    if not has_allowed_role(interaction.user):
        return await interaction.response.send_message("Nie masz uprawnień do używania tej komendy!", ephemeral=True)

    embed = discord.Embed(
        title="SAVAGE × OGŁOSZENIE",
        description=wiadomosc,
        color=0x2b2d31
    )
    embed.set_image(url=BANNER_URL)
    await kanal.send(embed=embed)
    await interaction.response.send_message(f"Wysłano wiadomość na kanał {kanal.mention}!", ephemeral=True)

@bot.tree.command(name="bandc", description="Baniuje użytkownika i czyści jego wiadomości")
@app_commands.describe(user="Użytkownik do zbanowania", powod="Powód bana")
async def bandc(interaction: discord.Interaction, user: discord.Member, powod: str = "Brak powodu"):
    if not has_allowed_role(interaction.user):
        return await interaction.response.send_message("Nie masz uprawnień do używania tej komendy!", ephemeral=True)

    await user.ban(reason=powod, delete_message_days=7)
    embed = discord.Embed(
        title="SAVAGE × BAN & CLEAR",
        description=f"Użytkownik {user.mention} został zbanowany, a jego wiadomości wyczyszczone.\n**Powód:** {powod}",
        color=0x2b2d31
    )
    embed.set_image(url=BANNER_URL)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="unbandc", description="Odbanowuje użytkownika")
@app_commands.describe(user_id="ID użytkownika do odbanowania", powod="Powód odbanowania")
async def unbandc(interaction: discord.Interaction, user_id: str, powod: str = "Brak powodu"):
    if not has_allowed_role(interaction.user):
        return await interaction.response.send_message("Nie masz uprawnień do używania tej komendy!", ephemeral=True)

    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user, reason=powod)
        embed = discord.Embed(
            title="SAVAGE × UNBAN",
            description=f"Użytkownik **{user.name}** (`{user.id}`) został odbanowany.\n**Powód:** {powod}",
            color=0x2b2d31
        )
        embed.set_image(url=BANNER_URL)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Nie udało się odbanować użytkownika. Błąd: {e}", ephemeral=True)

TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("CRITICAL ERROR: Brak zmiennej środowiskowej DISCORD_TOKEN!")