import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

COLDCFG_BANNER = "https://i.imgur.com/your_coldcfg_banner.png"
COLDCFG_BOOST_BANNER = "https://i.imgur.com/your_coldcfg_boosts.png"
THUMBNAIL_URL = "https://i.imgur.com/your_thumbnail.png"

WELCOME_CHANNEL_ID = 123456789012345678
BOOST_CHANNEL_ID = 123456789012345678

ROLE_VERIFIED_ID = 1540360249775493230

# ID RÓL DLA TICKETÓW
ROLE_OWNER_ID = 1556300080355606608
ROLE_SHOP_ID = 1556300130892906506
ROLE_SUPPORT_ID = 1556300180624769105
ROLE_RECRUITMENT_ID = 1556300236526329936
ROLE_PARTNER_ID = 1556383124424892606

# ID KATEGORII NA DISCORDZIE DLA TICKETÓW
CATEGORY_OWNER_ID = 123456789012345678
CATEGORY_SHOP_ID = 123456789012345678
CATEGORY_SUPPORT_ID = 123456789012345678
CATEGORY_RECRUITMENT_ID = 123456789012345678
CATEGORY_PARTNER_ID = 123456789012345678


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_VERIFIED_ID)
        if role:
            if role in interaction.user.roles:
                await interaction.response.send_message("❌ Jesteś już zweryfikowany!", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("✅ Pomyślnie zweryfikowano! Otrzymałeś dostęp do kanałów.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Błąd: Nie znaleziono roli do weryfikacji.", ephemeral=True)


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket 🔒", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Ten ticket zostanie zamknięty za 5 sekund...")
        await asyncio.sleep(5)
        await interaction.channel.delete()


class TicketSystemView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket_channel(self, interaction: discord.Interaction, ticket_type: str, role_id: int, category_id: int, emoji: str):
        guild = interaction.guild
        user = interaction.user
        role = guild.get_role(role_id)
        category = guild.get_channel(category_id)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        if role:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel_name = f"{emoji}-{ticket_type.lower()}-{user.name}"
        
        channel = await guild.create_text_channel(
            name=channel_name, 
            overwrites=overwrites, 
            category=category if isinstance(category, discord.CategoryChannel) else None
        )

        role_mention = role.mention if role else "@here"
        embed_color = 0xf1c40f if ticket_type == "Partnership" else 0x3498db

        embed = discord.Embed(
            title=f"🎫 Ticket - {ticket_type}",
            description=f"Witaj {user.mention}!\nOpisz swój problem lub zapytanie. Administracja niedługo Ci odpowie.",
            color=embed_color
        )
        
        await channel.send(content=f"{user.mention} {role_mention}", embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"✅ Twój ticket został utworzony: {channel.mention}", ephemeral=True)

    @discord.ui.button(label="Shop 🛒", style=discord.ButtonStyle.success, custom_id="btn_shop")
    async def shop_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "Shop", ROLE_SHOP_ID, CATEGORY_SHOP_ID, "🛒")

    @discord.ui.button(label="Owner 👑", style=discord.ButtonStyle.secondary, custom_id="btn_owner")
    async def owner_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "Owner", ROLE_OWNER_ID, CATEGORY_OWNER_ID, "👑")

    @discord.ui.button(label="Support ❓", style=discord.ButtonStyle.primary, custom_id="btn_support")
    async def support_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "Support", ROLE_SUPPORT_ID, CATEGORY_SUPPORT_ID, "❓")

    @discord.ui.button(label="Recruitment 📄", style=discord.ButtonStyle.danger, custom_id="btn_recruitment")
    async def recruitment_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "Recruitment", ROLE_RECRUITMENT_ID, CATEGORY_RECRUITMENT_ID, "📄")

    @discord.ui.button(label="Partnership 🤝", style=discord.ButtonStyle.secondary, custom_id="btn_partnership")
    async def partnership_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "Partnership", ROLE_PARTNER_ID, CATEGORY_PARTNER_ID, "🤝")


@bot.event
async def on_ready():
    print(f"✅ Coldcfg Bot zalogowany jako {bot.user.name}")
    bot.add_view(VerifyView())
    bot.add_view(TicketSystemView())
    bot.add_view(CloseTicketView())

    try:
        synced = await bot.tree.sync()
        print(f"⚡ Zsynchronizowano {len(synced)} komend slash.")
    except Exception as e:
        print(f"❌ Błąd synchronizacji komend: {e}")


@bot.tree.command(name="setup_weryfikacja", description="Tworzy panel weryfikacji na kanale.")
@app_commands.checks.has_permissions(administrator=True)
async def setup_weryfikacja(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Verification",
        description="Click on verification to get access to the channels",
        color=discord.Color.green()
    )
    await interaction.channel.send(embed=embed, view=VerifyView())
    await interaction.response.send_message("✅ Panel weryfikacji został wysłany!", ephemeral=True)


@bot.tree.command(name="setup_ticket", description="Tworzy panel wszystkich ticketów na kanale.")
@app_commands.checks.has_permissions(administrator=True)
async def setup_ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎟️ Tickets",
        description="Want to place an order, need to contact the owner or staff for help?\nClick the appropriate button below to open a private channel with the administration.\n\nPlease don't open the tickets without a proper reason.",
        color=0x3498db
    )
    await interaction.channel.send(embed=embed, view=TicketSystemView())
    await interaction.response.send_message("✅ Panel ticketów został wysłany!", ephemeral=True)


@bot.tree.command(name="minigame", description="Zagraj w minigrę i sprawdź swoje szczęście!")
async def minigame(interaction: discord.Interaction):
    win = random.randint(1, 35) == 1

    if win:
        embed = discord.Embed(
            title="🐱 Congratulations!",
            description=f"{interaction.user.mention}, **YOU WON!** 🎉\nYou hit the 1 in 35 chance!",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="🐱 We're sorry!",
            description=f"{interaction.user.mention}, **this time you didn't win anything.** Try your luck again tomorrow!\n\n**Some Info:**\n*Your chance was **1** in **35**.*\n\n*We wish you better luck next time!*",
            color=0x2b2d31
        )

    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_image(url=COLDCFG_BANNER)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="say", description="Wyślij wiadomość w czytelnej ramce (Embed).")
@app_commands.describe(wiadomosc="Treść wiadomości do wysłania")
async def say(interaction: discord.Interaction, wiadomosc: str):
    embed = discord.Embed(description=wiadomosc, color=0x2b2d31)
    embed.set_footer(text=f"Coldcfg • Today, Ad made by {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="bandc", description="Banuje użytkownika i tworzy raport o banie.")
@app_commands.describe(user="Użytkownik do zabanowania", reason="Powód bana")
@app_commands.checks.has_permissions(ban_members=True)
async def bandc(interaction: discord.Interaction, user: discord.Member, reason: str = "mrbeast"):
    embed = discord.Embed(title="🔨 User has been banned for life", color=discord.Color.red())
    embed.add_field(name="👤 User", value=user.mention, inline=True)
    embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=True)
    embed.add_field(name="🛡️ Administrator", value=interaction.user.mention, inline=False)
    embed.add_field(name="📝 Reason", value=f"```\n{reason}\n```", inline=False)
    embed.set_image(url=COLDCFG_BANNER)
    embed.set_footer(text="COLDCFG Security")

    try:
        await user.ban(reason=f"{reason} (Wystawił: {interaction.user})")
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Nie udało się zabanować: {e}", ephemeral=True)


@bot.event
async def on_member_join(member: discord.Member):
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        created_at = member.created_at.strftime("%d.%m.%Y %H:%M:%S")
        joined_at = member.joined_at.strftime("%d %B %Y %H:%M") if member.joined_at else "Now"

        embed = discord.Embed(
            title="New member!",
            description=f"🎉 Hi\n{member.mention}\nWelcome to the best cfg in Poland!\nGo check out our stuff!\n\n**You're our {member.guild.member_count} member!**\n\n**Member Info:**\n🪪 **Discord account created:**\n{created_at}\n👤 **Username:** `{member.name}`\n📅 **Joined at:** {joined_at}",
            color=0x2b2d31
        )
        embed.set_thumbnail(url=THUMBNAIL_URL)
        await channel.send(embed=embed)


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.premium_since is None and after.premium_since is not None:
        channel = after.guild.get_channel(BOOST_CHANNEL_ID)
        if channel:
            guild = after.guild
            embed = discord.Embed(
                title="⚙️ New server Boost!",
                description=f"{after.mention} **BOOST!**\n> thanks for boosting our server!\n> Go check out our booster zone!\n\n**Boost Info:**\n🧊 **Server Boost level:** `{guild.premium_tier}`\n🔢 **Boost count:** `{guild.premium_subscription_count}`",
                color=0xff73fa
            )
            embed.set_thumbnail(url=THUMBNAIL_URL)
            embed.set_image(url=COLDCFG_BOOST_BANNER)
            await channel.send(embed=embed)


TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ BŁĄD: Brak zmiennej DISCORD_TOKEN w Variables na Railway!")