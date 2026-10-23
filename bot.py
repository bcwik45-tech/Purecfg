import os
import discord
from discord.ext import commands
from discord import app_commands

# --- KONFIGURACJA ID I LINKÓW ---
BANNER_URL = "https://cdn.discordapp.com/attachments/1563303323539476520/1563303364106649620/savage_hallowen.jpg?ex=6add2336&is=6adbd1b6&hm=83cd3b66fa3da205eb25fef7fe2d6866d35a92f367982641f9343d95d6b00cdf&"

# Kanały
SETUP_CMD_CHANNEL_ID = 1561758533446410251
TICKET_PANEL_CHANNEL_ID = 1561742350986903702
WELCOME_CHANNEL_ID = 1561740336726937660
BOOST_CHANNEL_ID = 1563296339847282771

# Rola startowa dla nowych osób
AUTO_ROLE_ID = 1540360249775493230

# Role z uprawnieniami do komend (/setup_tickets, /say, /bandc, /unbandc)
ALLOWED_COMMAND_ROLES = [1540359821323149392, 1540495893399081061]

# Role do ticketów
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

        if category_name == "owner":
            ping_roles = OWNER_ROLES
            emoji_prefix = "👑"
        elif category_name == "partner":
            ping_roles = PARTNER_ROLES
            emoji_prefix = "🤝"
        elif category_name == "recruitment":
            ping_roles = RECRUITMENT_ROLES
            emoji_prefix = "📝"

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

        ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)

        pings_formatted = " ".join([f"<@&{r_id}>" for r_id in ping_roles])
        
        embed = discord.Embed(
            title=f"SAVAGE × {category_name.upper()}",
            description="Cześć witaj w savage opisz swoją sytuację",
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

# Auto-rola + Powitanie z bannerem
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

# Powiadomienia o Boostach
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

# --- KOMENDY SLASH Z WERYFIKACJĄ RÓL ---

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
            "│ **Ticket Owner**\n"
            "*Open if you have a demand to the owners*\n\n"
            "│ **Ticket Partner**\n"
            "*Open if you want to collaborate with us.*\n\n"
            "│ **Ticket Recruitment**\n"
            "*Open if you want to join our team*\n\n"
            f"│ **For any issues, text on** {chat_mention}"
        ),
        color=0x2b2d31
    )
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text="Savage")
    
    await target_channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message(f"Pomyślnie wysłano panel ticketów na kanał {target_channel.mention}!", ephemeral=True)

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