import discord
from discord.ext import commands
import os

# Konfiguracja intentów
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.bans = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- KONFIGURACJA ID ---
WELCOME_CHANNEL_ID = 1556280506516115466  # Kanał powitań
BANNER_URL = "https://i.imgur.com/8K5Q62x.png"  # Link do bannera Cold Cfg

# Kategorie ticketów
TICKET_CATEGORIES = {
    "shop": 1556300130892906506,
    "owner": 1556300080355606608,
    "support": 1556300180624769105,
    "recruitment": 1556300236526329936,
    "partner": 1556383124424892606
}

# Role mające dostęp do poszczególnych ticketów
TICKET_ROLES = {
    "shop": [1540359821323149392],
    "owner": [1540359821323149392, 1540495893399081061],
    "support": [1540359821323149392, 1540495893399081061, 1556062543963750400, 1540359905175801946, 1540360086617063584],
    "recruitment": [1540359821323149392, 1540495893399081061, 1556062543963750400, 1540359905175801946],
    "partner": [1540359821323149392, 1540495893399081061]
}

# Role nadawane przez komendę /accept
ACCEPT_ROLES = [1540359963346608168, 1540360086617063584]


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        guild = interaction.guild
        category_id = TICKET_CATEGORIES.get(ticket_type)
        category = guild.get_channel(category_id) if category_id else None
        allowed_role_ids = TICKET_ROLES.get(ticket_type, [])

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        for r_id in allowed_role_ids:
            role = guild.get_role(r_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        channel_name = f"ticket-{ticket_type}-{interaction.user.name}".lower()
        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

        role_pings = " ".join([f"<@&{r_id}>" for r_id in allowed_role_ids])

        embed = discord.Embed(
            title=f"Ticket: {ticket_type.upper()}",
            description=f"Witaj <@!{interaction.user.id}>!\nAdministracja wkrótce odpowie na Twoje zgłoszenie.",
            color=0x2b2d31
        )
        await ticket_channel.send(content=f"{role_pings} <@!{interaction.user.id}>", embeds=[embed])
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
    print(f"Zalogowano jako {bot.user.name}!")
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    try:
        synced = await bot.tree.sync()
        print(f"Zsynchronizowano {len(synced)} komend slash.")
    except Exception as e:
        print(e)


# --- POWITANIA ---
@bot.event
async def on_member_join(member: discord.Member):
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return

    created_at = f"<t:{int(member.created_at.timestamp())}:d> <t:{int(member.created_at.timestamp())}:T>"
    joined_at = f"<t:{int(member.joined_at.timestamp())}:d> <t:{int(member.joined_at.timestamp())}:T>"

    embed = discord.Embed(
        title="New member!",
        description=(
            f"🎉 Hi\n<@!{member.id}>\n"
            f"Welcome to the best cfg in Poland!\n"
            f"Go check out our stuff!\n\n"
            f"**You're our {member.guild.member_count} member!**\n\n"
            f"**Member Info:**\n"
            f"🪪 **Discord account created:**\n{created_at}\n"
            f"👤 **Username:** `{member.name}`\n"
            f"📅 **Joined at:** {joined_at}"
        ),
        color=0x2b2d31
    )
    avatar_url = member.guild.icon.url if member.guild.icon else member.display_avatar.url
    embed.set_thumbnail(url=avatar_url)

    await channel.send(embed=embed)


# --- BOOSTY ---
@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.premium_since is None and after.premium_since is not None:
        channel = after.guild.system_channel
        if not channel:
            return

        embed = discord.Embed(
            title="💎 New server Boost!",
            description=(
                f"<@!{after.id}> **BOOST!**\n"
                f"> thanks for boosting our server!\n"
                f"> Go check out our booster zone!\n\n"
                f"**Boost Info:**\n"
                f"🧊 Server Boost level: `{after.guild.premium_tier}`\n"
                f"🔢 Boost count: `{after.guild.premium_subscription_count}`"
            ),
            color=0xff73fa
        )
        embed.set_thumbnail(url=after.display_avatar.url)
        embed.set_image(url=BANNER_URL)

        await channel.send(embed=embed)


# --- KOMENDY SLASH ---

@bot.tree.command(name="say", description="Wysyła wiadomość jako embed")
async def say(interaction: discord.Interaction, message: str):
    embed = discord.Embed(description=message, color=0x2b2d31)
    embed.set_footer(text=f"{bot.user.name} • Today, Ad made by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="bandc", description="Banuje użytkownika")
@discord.app_commands.checks.has_permissions(ban_members=True)
async def bandc(interaction: discord.Interaction, target: discord.User, reason: str):
    await interaction.guild.ban(target, reason=reason)
    embed = discord.Embed(title="🔨 User has been banned for life", color=0xff0000)
    embed.add_field(name="👤 User", value=f"<@!{target.id}>", inline=True)
    embed.add_field(name="🆔 ID", value=f"`{target.id}`", inline=True)
    embed.add_field(name="🛡️ Administrator", value=f"<@!{interaction.user.id}>", inline=False)
    embed.add_field(name="📝 Reason", value=f"```\n{reason}\n```", inline=False)
    embed.set_image(url=BANNER_URL)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="unbandc", description="Odbanowuje użytkownika")
@discord.app_commands.checks.has_permissions(ban_members=True)
async def unbandc(interaction: discord.Interaction, userid: str, reason: str = "Brak powody"):
    user = await bot.fetch_user(int(userid))
    await interaction.guild.unban(user, reason=reason)
    embed = discord.Embed(title="🔓 User has been unbanned", color=0x00ff00)
    embed.add_field(name="👤 User", value=f"<@!{userid}>", inline=True)
    embed.add_field(name="🆔 ID", value=f"`{userid}`", inline=True)
    embed.add_field(name="🛡️ Administrator", value=f"<@!{interaction.user.id}>", inline=False)
    embed.add_field(name="📝 Reason", value=f"```\n{reason}\n```", inline=False)
    embed.set_image(url=BANNER_URL)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="minigame", description="Losowanie nagrody w Cold Cfg")
async def minigame(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🐱 We're sorry!",
        description=(
            f"<@!{interaction.user.id}>, this time you didn't win anything. Try your luck again tomorrow!\n\n"
            f"**Some Info:**\n"
            f"*Your chance was* **1** *in* **35**.\n\n"
            f"*We wish you better luck next time!*"
        ),
        color=0x2b2d31
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_image(url=BANNER_URL)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="accept", description="Accept candidate and give roles")
@discord.app_commands.checks.has_permissions(manage_roles=True)
async def accept(interaction: discord.Interaction, target: discord.Member):
    for r_id in ACCEPT_ROLES:
        role = interaction.guild.get_role(r_id)
        if role:
            await target.add_roles(role)
    await interaction.response.send_message(f"Pomyślnie nadano role użytkownikowi <@!{target.id}>!", ephemeral=True)


@bot.tree.command(name="setup", description="Wysyła panele weryfikacji i ticketów")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    verify_embed = discord.Embed(
        title="Verification",
        description="Click on verification to get access to the channels",
        color=0x2ecc71
    )
    await interaction.channel.send(embed=verify_embed, view=VerifyView())

    ticket_embed = discord.Embed(
        title="🎫 Tickets",
        description=(
            "Want to place an order, need to contact the owner or staff for help?\n"
            "Click the appropriate button below to open a private channel with the administration.\n\n"
            "Please don't open the tickets without a proper reason."
        ),
        color=0x3498db
    )
    await interaction.channel.send(embed=ticket_embed, view=TicketView())
    await interaction.response.send_message("Wysłano panele!", ephemeral=True)


bot.run(os.getenv("DISCORD_TOKEN"))