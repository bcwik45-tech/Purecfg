import os
import asyncio
from datetime import datetime
from threading import Thread

import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask

# ==========================================
# KEEP-ALIVE SERVER FOR UPTIMEROBOT / RENDER
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "KyroCFG Bot Status: Online"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ==========================================
# BOT SETUP & CONSTANTS
# ==========================================
BANNER_URL = "https://cdn.discordapp.com/attachments/1561758533446410251/1568729185751671017/-_by_fin__3.jpg?ex=6af0e067&is=6aef8ee7&hm=f46719c8121b22952f76a25d02c8d82a489d8f2b93e30ad0c11080cf709a07a0&"

# Emotikony powitań
W_EMOJI = [
    "https://cdn.discordapp.com/emojis/1568728427865841805.webp?size=96", # 1
    "https://cdn.discordapp.com/emojis/1568728735765504120.webp?size=96", # 2
    "https://cdn.discordapp.com/emojis/1568728589036163264.webp?size=96", # 3
    "https://cdn.discordapp.com/emojis/1568727905465401464.webp?size=96", # 4
    "https://cdn.discordapp.com/emojis/1567488704979669003.webp?size=96", # 5
    "https://cdn.discordapp.com/emojis/1568728280603951195.webp?size=96"  # 6
]

# Emotikony boostów
B_EMOJI = [
    "https://cdn.discordapp.com/emojis/1567489885365997638.webp?size=96", # 1
    "https://cdn.discordapp.com/emojis/1567489688032256041.webp?size=96", # 2
    "https://cdn.discordapp.com/emojis/1567490142908719155.webp?size=96", # 3
    "https://cdn.discordapp.com/emojis/1568728280603951195.webp?size=96"  # 4
]

# Kanały i Kategorie
WELCOME_CHANNEL_ID = 1561740336726937660
TICKETS_CMD_CHANNEL_ID = 1561758533446410251
PANEL_TARGET_CHANNEL_ID = 1568723558069440582

# Konfiguracje Ticketów
TICKET_CONFIGS = {
    "owner": {
        "label": "Ticket Owner",
        "desc": "Open if you have a demand to the owners",
        "category_id": 1567496735360811049,
        "access_roles": [1540359821323149392, 1540495893399081061],
        "icon": "👑",
        "style": discord.ButtonStyle.danger # Czerwony
    },
    "support": {
        "label": "Ticket Support",
        "desc": "Open if you need any help",
        "category_id": 1567497448379645984,
        "access_roles": [1568725620601524254],
        "icon": "🛠️",
        "style": discord.ButtonStyle.success # Zielony
    },
    "shop": {
        "label": "Ticket Shop",
        "desc": "Open if you want to buy something",
        "category_id": 1567497043134386226,
        "access_roles": [1540359821323149392],
        "icon": "🛒",
        "style": discord.ButtonStyle.primary # Niebieski
    },
    "partner": {
        "label": "Ticket Partner",
        "desc": "Open if you want to collaborate with us.",
        "category_id": 1568731769782534374,
        "access_roles": [1568725620601524254],
        "icon": "🤝",
        "style": discord.ButtonStyle.secondary # Żółty / Szary w discord.py API
    }
}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# VIEWS & BUTTONS (TICKETS)
# ==========================================
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="kyro_close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        channel = interaction.channel
        
        # Pobranie historii wiadomości do transkryptu
        messages = []
        async for msg in channel.history(limit=500, oldest_first=True):
            time_str = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            messages.append(f"[{time_str}] {msg.author} ({msg.author.id}): {msg.clean_content}")
            
        transcript_text = "\n".join(messages)
        
        # Tworzenie pliku tekstowego
        file_path = f"transcript-{channel.name}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"TRANSCRIPT FOR TICKET: {channel.name}\n")
            f.write(f"Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
            f.write("="*50 + "\n\n")
            f.write(transcript_text)

        # Znalezienie twórcy ticketu z nazwy kanału lub wzmianek
        ticket_opener = None
        for member in channel.members:
            if not member.bot and member.name.lower() in channel.name:
                ticket_opener = member
                break
        if not ticket_opener:
            ticket_opener = interaction.user

        # Wysyłanie transkryptu na PV twórcy
        try:
            with open(file_path, "rb") as f:
                discord_file = discord.File(f, filename=file_path)
                embed = discord.Embed(
                    title="📜 Ticket Transcript",
                    description=f"Oto transkrypt Twojego ticketu z kanału **#{channel.name}**.",
                    color=discord.Color.dark_gray()
                )
                embed.set_footer(text="Kyro")
                await ticket_opener.send(embed=embed, file=discord_file)
        except Exception as e:
            print(f"Nie udało się wysłać transkryptu na PV: {e}")

        # Usunięcie tymczasowego pliku z dysku
        if os.path.exists(file_path):
            os.remove(file_path)

        await channel.send("🔒 Ticket zostanie usunięty za 5 sekund...")
        await asyncio.sleep(5)
        await channel.delete()


class TicketControlPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Owner", style=discord.ButtonStyle.danger, custom_id="ticket_btn_owner")
    async def owner_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "owner")

    @discord.ui.button(label="Support", style=discord.ButtonStyle.success, custom_id="ticket_btn_support")
    async def support_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "support")

    @discord.ui.button(label="Shop", style=discord.ButtonStyle.primary, custom_id="ticket_btn_shop")
    async def shop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "shop")

    @discord.ui.button(label="Partner", style=discord.ButtonStyle.secondary, custom_id="ticket_btn_partner")
    async def partner_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "partner")


async def create_ticket(interaction: discord.Interaction, ticket_type: str):
    guild = interaction.guild
    user = interaction.user
    cfg = TICKET_CONFIGS[ticket_type]

    category = guild.get_channel(cfg["category_id"])
    if not category:
        await interaction.response.send_message("❌ Błąd: Kategoria ticketów nie istnieje.", ephemeral=True)
        return

    # Ustawianie uprawnień
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
    }

    for role_id in cfg["access_roles"]:
        role = guild.get_role(role_id)
        if role:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    channel_name = f"{ticket_type}-{user.name}"
    channel = await guild.create_text_channel(
        name=channel_name,
        category=category,
        overwrites=overwrites
    )

    await interaction.response.send_message(f"✅ Stworzono ticket: {channel.mention}", ephemeral=True)

    # Wiadomość powitalna wewnątrz otwieranego ticketu
    pings = " ".join([f"<@&{r_id}>" for r_id in cfg["access_roles"]])
    embed = discord.Embed(
        description=f"• **{ticket_type.upper()}** {cfg['icon']}\n\n"
                    f"**Open date:** {datetime.utcnow().strftime('%d %B %Y, %H:%M')}\n"
                    f"**Opening user:** {user.mention}\n\n"
                    f"**Description:** Please give us details about your reason to open this ticket.\n"
                    f"Click the button below to close the ticket.",
        color=discord.Color.dark_gray()
    )
    embed.set_footer(text="Kyro")

    await channel.send(content=f"{pings} {user.mention}", embed=embed, view=CloseTicketView())

# ==========================================
# EVENTS & COMMANDS
# ==========================================
@bot.event
async def on_ready():
    print(f"[-] Bot Kyro online: {bot.user}")
    bot.add_view(TicketControlPanel())
    bot.add_view(CloseTicketView())
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

# Powitania użytkowników
@bot.event
async def on_member_join(member: discord.Member):
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return

    # Przygotowanie pól z emotikonami po bokach
    member_count = member.guild.member_count
    created_at = member.created_at.strftime("%Y-%m-%d %H:%M:%S")
    joined_at = member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    hi_val = f"<{W_EMOJI[0]}> Hi {member.mention} We're glad to have you here! <{W_EMOJI[1]}>\nGo check out our fivem stuff!\nDon't forget to read the rules!\n**You're our {member_count} member!**"
    user_info_val = f"<{W_EMOJI[2]}> **Discord account created:** `{created_at}` <{W_EMOJI[3]}>\n<{W_EMOJI[4]}> **Username:** `{member.name}` <{W_EMOJI[5]}>\n<{W_EMOJI[0]}> **Joined at:** `{joined_at}` <{W_EMOJI[1]}>"

    embed = discord.Embed(color=discord.Color.dark_gray())
    embed.add_field(name=" ", value=hi_val, inline=False)
    embed.add_field(name="📣 User Information", value=user_info_val, inline=False)
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text="Kyro")

    # Wymagany duży nagłówek na samej górze
    await channel.send(content="# New user joined us!", embed=embed)

# Wykrywanie Boostów serwera
@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if not before.premium_since and after.premium_since:
        channel = after.guild.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return

        boost_level = after.guild.premium_tier
        boost_count = after.guild.premium_subscription_count

        boost_val = f"<{B_EMOJI[0]}> {after.mention} **BOOST!** <{B_EMOJI[1]}>\nthanks for boosting our server!\n*Go check out our booster zone!*\n\n" \
                    f"🚀 **Boost level**\n<{B_EMOJI[2]}> **Server Boost level:** `{boost_level}` <{B_EMOJI[3]}>\n<{B_EMOJI[0]}> **Boost count:** `{boost_count}` <{B_EMOJI[1]}>"

        embed = discord.Embed(title="⬡ New server Boost!", description=boost_val, color=discord.Color.dark_gray())
        embed.set_thumbnail(url=after.display_avatar.url)
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text="Kyro")

        await channel.send(embed=embed)

# Komenda /tickets
@bot.tree.command(name="tickets", description="Generuje panel ticketów na wyznaczonym kanale")
async def tickets_cmd(interaction: discord.Interaction):
    if interaction.channel_id != TICKETS_CMD_CHANNEL_ID:
        await interaction.response.send_message("❌ Tej komendy możesz użyć tylko na przeznaczonym do tego kanale.", ephemeral=True)
        return

    target_channel = interaction.guild.get_channel(PANEL_TARGET_CHANNEL_ID)
    if not target_channel:
        await interaction.response.send_message("❌ Kanał docelowy dla panelu nie istnieje.", ephemeral=True)
        return

    embed = discord.Embed(title="Tickets", color=discord.Color.dark_gray())
    
    for key, item in TICKET_CONFIGS.items():
        embed.add_field(
            name=f"|  {item['label']}",
            value=f"*{item['desc']}*",
            inline=False
        )

    embed.add_field(name="|  For any issues, text on #chat", value="\u200b", inline=False)
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text="Kyro")

    await target_channel.send(embed=embed, view=TicketControlPanel())
    await interaction.response.send_message(f"✅ Panel ticketów został wysłany na {target_channel.mention}", ephemeral=True)

# Komenda /bandc
@bot.tree.command(name="bandc", description="Banuje użytkownika i wysyła zgłoszenie")
@app_commands.describe(user="Użytkownik do zbanowania", reason="Powód bana")
async def bandc_cmd(interaction: discord.Interaction, user: discord.Member, reason: str):
    await interaction.guild.ban(user, reason=reason)

    embed = discord.Embed(title="🔨 User banned permanently", color=discord.Color.red())
    embed.add_field(name="👤 User", value=user.mention, inline=False)
    embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=False)
    embed.add_field(name="🛡️ Administrator", value=interaction.user.mention, inline=False)
    embed.add_field(name="📝 Reason", value=f"```\n{reason}\n```", inline=False)

    embed.set_thumbnail(url=BANNER_URL)
    embed.set_footer(text=f"Kyro Security • {datetime.utcnow().strftime('%d listopada %Y %H:%M')}")

    await interaction.response.send_message(embed=embed)

# Komenda /unbandc
@bot.tree.command(name="unbandc", description="Odbanowuje użytkownika")
@app_commands.describe(user_id="ID użytkownika do odbanowania", reason="Powód odbanowania")
async def unbandc_cmd(interaction: discord.Interaction, user_id: str, reason: str):
    user = await bot.fetch_user(int(user_id))
    await interaction.guild.unban(user, reason=reason)

    embed = discord.Embed(title="🔓 User unbanned", color=discord.Color.green())
    embed.add_field(name="👤 User", value=f"{user.name} ({user.mention})", inline=False)
    embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=False)
    embed.add_field(name="🛡️ Administrator", value=interaction.user.mention, inline=False)
    embed.add_field(name="📝 Reason", value=f"```\n{reason}\n```", inline=False)

    embed.set_thumbnail(url=BANNER_URL)
    embed.set_footer(text=f"Kyro Security • {datetime.utcnow().strftime('%d listopada %Y %H:%M')}")

    await interaction.response.send_message(embed=embed)

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ Ustaw zmienną środowiskową DISCORD_TOKEN na Render / GitHub Secrets!")