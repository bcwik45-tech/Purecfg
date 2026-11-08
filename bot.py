import os
import asyncio
from datetime import datetime
from threading import Thread

import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask

# ==========================================
# KEEP-ALIVE SERVER (Dla UptimeRobot / Render)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "GoatCFG Bot Status: Online"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ==========================================
# STAŁE I KONFIGURACJA
# ==========================================
BANNER_URL = "https://cdn.discordapp.com/attachments/1561758533446410251/1568729185751671017/-_by_fin__3.jpg?ex=6af0e067&is=6aef8ee7&hm=f46719c8121b22952f76a25d02c8d82a489d8f2b93e30ad0c11080cf709a07a0&"

W_EMOJI = [
    "https://cdn.discordapp.com/emojis/1568728427865841805.webp?size=96",
    "https://cdn.discordapp.com/emojis/1568728735765504120.webp?size=96",
    "https://cdn.discordapp.com/emojis/1568728589036163264.webp?size=96",
    "https://cdn.discordapp.com/emojis/1568727905465401464.webp?size=96",
    "https://cdn.discordapp.com/emojis/1567488704979669003.webp?size=96",
    "https://cdn.discordapp.com/emojis/1568728280603951195.webp?size=96"
]

B_EMOJI = [
    "https://cdn.discordapp.com/emojis/1567489885365997638.webp?size=96",
    "https://cdn.discordapp.com/emojis/1567489688032256041.webp?size=96",
    "https://cdn.discordapp.com/emojis/1567490142908719155.webp?size=96",
    "https://cdn.discordapp.com/emojis/1568728280603951195.webp?size=96"
]

WELCOME_CHANNEL_ID = 1561740336726937660
TICKETS_CMD_CHANNEL_ID = 1561758533446410251
PANEL_TARGET_CHANNEL_ID = 1568723558069440582

TICKET_CONFIGS = {
    "owner": {
        "label": "Ticket Owner",
        "desc": "Open if you have a demand to the owners",
        "category_id": 1567496735360811049,
        "access_roles": [1540359821323149392, 1540495893399081061],
        "icon": "👑"
    },
    "shop": {
        "label": "Ticket Shop",
        "desc": "open if you you want to buy something",
        "category_id": 1567497043134386226,
        "access_roles": [1540359821323149392],
        "icon": "🛒"
    },
    "support": {
        "label": "Ticket Support",
        "desc": "Open if you need any help",
        "category_id": 1567497448379645984,
        "access_roles": [1568725620601524254],
        "icon": "🛠️"
    },
    "partner": {
        "label": "Ticket Partner",
        "desc": "Open if you want to collaborate with us.",
        "category_id": 1568731769782534374,
        "access_roles": [1568725620601524254],
        "icon": "🤝"
    }
}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="goat_close_ticket_clean")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        channel = interaction.channel
        
        messages = []
        async for msg in channel.history(limit=500, oldest_first=True):
            time_str = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            messages.append(f"[{time_str}] {msg.author} ({msg.author.id}): {msg.clean_content}")
            
        transcript_text = "\n".join(messages)
        file_path = f"transcript-{channel.name}.txt"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"TRANSCRIPT FOR TICKET: {channel.name}\n")
            f.write(f"Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
            f.write("="*50 + "\n\n")
            f.write(transcript_text)

        ticket_opener = None
        for member in channel.members:
            if not member.bot and member.name.lower() in channel.name:
                ticket_opener = member
                break
        if not ticket_opener:
            ticket_opener = interaction.user

        try:
            with open(file_path, "rb") as f:
                discord_file = discord.File(f, filename=file_path)
                embed = discord.Embed(
                    title="📜 Ticket Transcript",
                    description=f"Oto transkrypt Twojego ticketu z kanału **#{channel.name}**.",
                    color=discord.Color.dark_gray()
                )
                embed.set_footer(text="Goatcfg")
                await ticket_opener.send(embed=embed, file=discord_file)
        except Exception as e:
            print(f"Nie udało się wysłać transkryptu na PV: {e}")

        if os.path.exists(file_path):
            os.remove(file_path)

        await channel.send("🔒 Ticket zostanie usunięty za 5 sekund...")
        await asyncio.sleep(5)
        await channel.delete()


class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Ticket Owner", description="Open if you have a demand to the owners", emoji="👑", value="owner"),
            discord.SelectOption(label="Ticket Shop", description="open if you you want to buy something", emoji="🛒", value="shop"),
            discord.SelectOption(label="Ticket Support", description="Open if you need any help", emoji="🛠️", value="support"),
            discord.SelectOption(label="Ticket Partner", description="Open if you want to collaborate with us.", emoji="🤝", value="partner")
        ]
        super().__init__(placeholder="➔ Select category...", min_values=1, max_values=1, options=options, custom_id="goat_ticket_select_clean")

    async def callback(self, interaction: discord.Interaction):
        ticket_type = self.values[0]
        await create_ticket(interaction, ticket_type)


class TicketSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


async def create_ticket(interaction: discord.Interaction, ticket_type: str):
    guild = interaction.guild
    user = interaction.user
    cfg = TICKET_CONFIGS[ticket_type]

    category = guild.get_channel(cfg["category_id"])
    if not category:
        await interaction.response.send_message("❌ Błąd: Kategoria ticketów nie została skonfigurowana.", ephemeral=True)
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
    }

    for role_id in cfg["access_roles"]:
        role = guild.get_role(role_id)
        if role:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    channel_name = f"{cfg['icon']}-{ticket_type}-{user.name}"
    channel = await guild.create_text_channel(
        name=channel_name,
        category=category,
        overwrites=overwrites
    )

    await interaction.response.send_message(f"✅ Stworzono ticket: {channel.mention}", ephemeral=True)

    pings = " ".join([f"<@&{r_id}>" for r_id in cfg["access_roles"]])
    embed = discord.Embed(
        description=f"• **{ticket_type.upper()}** {cfg['icon']}\n\n"
                    f"**Open date:** {datetime.utcnow().strftime('%d %B %Y, %H:%M')}\n"
                    f"**Opening user:** {user.mention}\n\n"
                    f"**Description:** Please give us details about your reason to open this ticket.\n"
                    f"Click the button below to close the ticket.",
        color=discord.Color.dark_gray()
    )
    embed.set_footer(text="Goatcfg")

    await channel.send(content=f"{pings} {user.mention}", embed=embed, view=CloseTicketView())


@bot.event
async def on_ready():
    print(f"[-] Bot Goatcfg online: {bot.user}")
    bot.add_view(TicketSelectView())
    bot.add_view(CloseTicketView())
    try:
        synced = await bot.tree.sync()
        print(f"Zsynchronizowano pomyślnie {len(synced)} komend slash.")
    except Exception as e:
        print(f"Błąd synchronizacji komend slash: {e}")


@bot.event
async def on_member_join(member: discord.Member):
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return

    member_count = member.guild.member_count
    created_at = member.created_at.strftime("%Y-%m-%d %H:%M:%S")
    joined_at = member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    hi_val = f"<{W_EMOJI[0]}> Hi {member.mention} We're glad to have you here! <{W_EMOJI[1]}>\n" \
             f"Go check out our fivem stuff!\n" \
             f"Don't forget to read the rules!\n" \
             f"**You're our {member_count} member!**"
             
    user_info_val = f"<{W_EMOJI[2]}> **Discord account created:** `{created_at}` <{W_EMOJI[3]}>\n" \
                    f"<{W_EMOJI[4]}> **Username:** `{member.name}` <{W_EMOJI[5]}>\n" \
                    f"<{W_EMOJI[0]}> **Joined at:** `{joined_at}` <{W_EMOJI[1]}>"

    embed = discord.Embed(color=discord.Color.dark_gray())
    embed.add_field(name=" ", value=hi_val, inline=False)
    embed.add_field(name="📣 User Information", value=user_info_val, inline=False)
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text="Goatcfg")

    await channel.send(content="# New user joined us!", embed=embed)


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if not before.premium_since and after.premium_since:
        channel = after.guild.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return

        boost_level = after.guild.premium_tier
        boost_count = after.guild.premium_subscription_count

        boost_val = f"<{B_EMOJI[0]}> {after.mention} **BOOST!** <{B_EMOJI[1]}>\nthanks for boosting our server!\n*Go check out our booster zone!*\n\n" \
                    f"🚀 **Boost level**\n" \
                    f"<{B_EMOJI[2]}> **Server Boost level:** `{boost_level}` <{B_EMOJI[3]}>\n" \
                    f"<{B_EMOJI[0]}> **Boost count:** `{boost_count}` <{B_EMOJI[1]}>"

        embed = discord.Embed(title="⬡ New server Boost!", description=boost_val, color=discord.Color.dark_gray())
        embed.set_thumbnail(url=after.display_avatar.url)
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text="Goatcfg")

        await channel.send(embed=embed)


@bot.tree.command(name="tickets", description="Wysyła panel ticketów na wskazany kanał")
async def tickets_cmd(interaction: discord.Interaction):
    if interaction.channel_id != TICKETS_CMD_CHANNEL_ID:
        await interaction.response.send_message("❌ Tę komendę możesz wywołać tylko na dedykowanym kanale.", ephemeral=True)
        return

    target_channel = interaction.guild.get_channel(PANEL_TARGET_CHANNEL_ID)
    if not target_channel:
        await interaction.response.send_message("❌ Nie znaleziono docelowego kanału dla panelu ticketów.", ephemeral=True)
        return

    embed = discord.Embed(title="Tickets", color=discord.Color.dark_gray())
    embed.add_field(name="│  Ticket Owner", value="*Open if you have a demand to the owners*", inline=False)
    embed.add_field(name="│  Ticket Shop", value="*open if you you want to buy something*", inline=False)
    embed.add_field(name="│  Ticket Support", value="*Open if you need any help*", inline=False)
    embed.add_field(name="│  Ticket Partner", value="*Open if you want to collaborate with us.*", inline=False)
    embed.add_field(name="│  For any issues, text on #chat", value="\u200b", inline=False)

    embed.set_image(url=BANNER_URL)
    embed.set_footer(text="Goatcfg")

    try:
        async for old_msg in target_channel.history(limit=15):
            if old_msg.author == bot.user:
                await old_msg.delete()
    except Exception as e:
        print(f"Nie można usunąć starej wiadomości: {e}")

    await target_channel.send(embed=embed, view=TicketSelectView())
    await interaction.response.send_message(f"✅ Panel wysłany pomyślnie na kanał {target_channel.mention}", ephemeral=True)


@bot.tree.command(name="bandc", description="Banuje użytkownika i wysyła log banów")
@app_commands.describe(user="Użytkownik do zbanowania", reason="Powód bana")
async def bandc_cmd(interaction: discord.Interaction, user: discord.Member, reason: str):
    await interaction.guild.ban(user, reason=reason)

    embed = discord.Embed(title="🔨 User banned permanently", color=discord.Color.red())
    embed.add_field(name="👤 User", value=user.mention, inline=False)
    embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=False)
    embed.add_field(name="🛡️ Administrator", value=interaction.user.mention, inline=False)
    embed.add_field(name="📝 Reason", value=f"```\n{reason}\n```", inline=False)

    embed.set_thumbnail(url=BANNER_URL)
    embed.set_footer(text=f"Goat Security • {datetime.utcnow().strftime('%d listopada %Y %H:%M')}")

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="unbandc", description="Odbanowuje użytkownika po ID")
@app_commands.describe(user_id="ID użytkownika", reason="Powód odbanowania")
async def unbandc_cmd(interaction: discord.Interaction, user_id: str, reason: str):
    user = await bot.fetch_user(int(user_id))
    await interaction.guild.unban(user, reason=reason)

    embed = discord.Embed(title="🔓 User unbanned", color=discord.Color.green())
    embed.add_field(name="👤 User", value=f"{user.name} ({user.mention})", inline=False)
    embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=False)
    embed.add_field(name="🛡️ Administrator", value=interaction.user.mention, inline=False)
    embed.add_field(name="📝 Reason", value=f"```\n{reason}\n```", inline=False)

    embed.set_thumbnail(url=BANNER_URL)
    embed.set_footer(text=f"Goat Security • {datetime.utcnow().strftime('%d listopada %Y %H:%M')}")

    await interaction.response.send_message(embed=embed)


if __name__ == "__main__":
    keep_alive()
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ Brak zmiennej środowiskowej DISCORD_TOKEN!")