import discord
from discord.ext import commands, tasks
from discord import app_commands
import random
import asyncio
import os
from datetime import date

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

COLDCFG_BANNER = "https://i.imgur.com/your_coldcfg_banner.png"
MINIGAME_BANNER = "TUTAJ_WKLEJ_LINK_DO_OBRAZKA_Z_NAPISEM_COLDCFG"
COLDCFG_BOOST_BANNER = "https://i.imgur.com/your_coldcfg_boosts.png"
THUMBNAIL_URL = "https://i.imgur.com/your_thumbnail.png"

# ==========================================
# ID KANAŁÓW POWITAŃ I BOOSTÓW
# ==========================================
WELCOME_CHANNEL_ID = 1556280506516115466
BOOST_CHANNEL_ID = 1540358387219304592

MINIGAME_CHANNEL_ID = 1556566161653764157
MINIGAME_WIN_ROLE_ID = 1556565240832073779

ROLE_VERIFIED_ID = 1540360249775493230

# ==========================================
# LISTY RÓL DLA POSZCZEGÓLNYCH TICKETÓW
# ==========================================
ROLES_OWNER = [1540359821323149392, 1540495893399081061]
ROLES_SHOP = [1540359821323149392]
ROLES_SUPPORT = [1540360086617063584, 1540359905175801946, 1556062543963750400, 1540495893399081061, 1540359821323149392]
ROLES_RECRUITMENT = [1540359821323149392, 1540495893399081061, 1556062543963750400, 1540359905175801946]
ROLES_PARTNER = [1540359821323149392, 1540495893399081061]

# ==========================================
# ID KATEGORII NA DISCORDZIE DLA TICKETÓW
# ==========================================
CATEGORY_OWNER_ID = 1556300080355606608
CATEGORY_SHOP_ID = 1556300130892906506
CATEGORY_SUPPORT_ID = 1556300180624769105
CATEGORY_RECRUITMENT_ID = 1556300236526329936
CATEGORY_PARTNER_ID = 1556383124424892606

minigame_cooldowns = {}


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        role = interaction.guild.get_role(ROLE_VERIFIED_ID)
        if role:
            if role in interaction.user.roles:
                await interaction.followup.send("❌ Jesteś już zweryfikowany!", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.followup.send("✅ Pomyślnie zweryfikowano! Otrzymałeś dostęp do kanałów.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Błąd: Nie znaleziono roli do weryfikacji.", ephemeral=True)


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

    async def create_ticket_channel(self, interaction: discord.Interaction, ticket_type: str, role_ids: list, category_id: int, emoji: str):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        user = interaction.user
        category = guild.get_channel(category_id)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        roles_mentions = []
        for r_id in role_ids:
            role = guild.get_role(r_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                roles_mentions.append(role.mention)

        channel_name = f"{emoji}-{ticket_type.lower()}-{user.name}"
        target_category = category if isinstance(category, discord.CategoryChannel) else None

        channel = await guild.create_text_channel(
            name=channel_name, 
            overwrites=overwrites, 
            category=target_category
        )

        role_ping_str = " ".join(roles_mentions) if roles_mentions else "@here"
        embed_color = 0xf1c40f if ticket_type == "Partnership" else 0x3498db

        embed = discord.Embed(
            title=f"🎫 Ticket - {ticket_type}",
            description=f"Witaj {user.mention}!\nOpisz swój problem lub zapytanie. Administracja niedługo Ci odpowie.",
            color=embed_color
        )
        
        await channel.send(content=f"{user.mention} {role_ping_str}", embed=embed, view=CloseTicketView())
        await interaction.followup.send(f"✅ Twój ticket został utworzony: {channel.mention}", ephemeral=True)

    @discord.ui.button(label="Shop 🛒", style=discord.ButtonStyle.success, custom_id="btn_shop")
    async def shop_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "Shop", ROLES_SHOP, CATEGORY_SHOP_ID, "🛒")

    @discord.ui.button(label="Owner 👑", style=discord.ButtonStyle.secondary, custom_id="btn_owner")
    async def owner_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "Owner", ROLES_OWNER, CATEGORY_OWNER_ID, "👑")

    @discord.ui.button(label="Support ❓", style=discord.ButtonStyle.primary, custom_id="btn_support")
    async def support_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "Support", ROLES_SUPPORT, CATEGORY_SUPPORT_ID, "❓")

    @discord.ui.button(label="Recruitment 📄", style=discord.ButtonStyle.danger, custom_id="btn_recruitment")
    async def recruitment_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "Recruitment", ROLES_RECRUITMENT, CATEGORY_RECRUITMENT_ID, "📄")

    @discord.ui.button(label="Partnership 🤝", style=discord.ButtonStyle.secondary, custom_id="btn_partnership")
    async def partnership_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "Partnership", ROLES_PARTNER, CATEGORY_PARTNER_ID, "🤝")


@tasks.loop(hours=2)
async def minigame_reminder():
    channel = bot.get_channel(MINIGAME_CHANNEL_ID)
    if channel:
        guild = channel.guild
        role = guild.get_role(ROLE_VERIFIED_ID)
        role_ping = role.mention if role else f"<@&{ROLE_VERIFIED_ID}>"

        embed = discord.Embed(
            title="🎮 Daily Minigame Reminder!",
            description="Hey everyone! Don't forget to test your luck today with `/minigame`! Win amazing rewards and a special role!",
            color=0x3498db
        )
        embed.set_image(url=MINIGAME_BANNER)
        await channel.send(content=role_ping, embed=embed)

@minigame_reminder.before_loop
async def before_minigame_reminder():
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    print(f"✅ Coldcfg Bot zalogowany jako {bot.user.name}")
    bot.add_view(VerifyView())
    bot.add_view(TicketSystemView())
    bot.add_view(CloseTicketView())
    
    if not minigame_reminder.is_running():
        minigame_reminder.start()

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
    if interaction.channel.id != MINIGAME_CHANNEL_ID:
        await interaction.response.send_message(f"❌ Tej komendy można używać wyłącznie na kanale <#{MINIGAME_CHANNEL_ID}>!", ephemeral=True)
        return

    await interaction.response.defer()

    today = date.today()
    if minigame_cooldowns.get(interaction.user.id) == today:
        await interaction.followup.send("❌ Wykorzystałeś już swoją dzisiejszą próbę w minigrze! Spróbuj ponownie jutro (cooldown odnawia się o północy).", ephemeral=True)
        return

    minigame_cooldowns[interaction.user.id] = today

    win = random.randint(1, 35) == 1

    if win:
        role = interaction.guild.get_role(MINIGAME_WIN_ROLE_ID)
        if role:
            try:
                await interaction.user.add_roles(role)
            except Exception:
                pass

        embed = discord.Embed(
            title="🐱 Congratulations!",
            description=f"{interaction.user.mention}, **YOU WON!** 🎉\nYou hit the 1 in 35 chance and received a special role!",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="🐱 We're sorry!",
            description=f"{interaction.user.mention}, **this time you didn't win anything.** Try your luck again tomorrow!\n\n**Some Info:**\n*Your chance was **1** in **35**.*\n\n*We wish you better luck next time!*",
            color=0x2b2d31
        )

    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_image(url=MINIGAME_BANNER)
    
    await interaction.followup.send(embed=embed)


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

        desc = (
            "🎉 Hi\n" + member.mention + "\n"
            "Welcome to the best cfg in Poland!\n"
            "Go check out our stuff!\n\n"
            "**You're our " + str(member.guild.member_count) + " member!**\n\n"
            "**Member Info:**\n"
            "🪪 **Discord account created:**\n" + created_at + "\n"
            "👤 **Username:** `" + member.name + "`\n"
            "📅 **Joined at:** " + joined_at
        )

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
        if channel:
            guild = after.guild
            
            boost_desc = (
                f"{after.mention} **BOOST!**\n"
                "> thanks for boosting our server!\n"
                "> Go check out our booster zone!\n\n"
                "**Boost Info:**\n"
                f"🧊 **Server Boost level:** `{guild.premium_tier}`\n"
                f"🔢 **Boost count:** `{guild.premium_subscription_count}`"
            )
            
            embed = discord.Embed(
                title="⚙️ New server Boost!",
                description=boost_desc,
                color=0xff73fa
            )
            embed.set_thumbnail(url=after.display_avatar.url)
            embed.set_image(url=COLDCFG_BOOST_BANNER)
            await channel.send(embed=embed)


TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ BŁĄD: Brak zmiennej DISCORD_TOKEN w Variables na Railway!")