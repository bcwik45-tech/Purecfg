import os
import discord
from discord import app_commands
from discord.ext import commands

# Konfiguracja intencji - używamy all(), aby uniknąć problemów z wersjami discord.py
intents = discord.Intents.all()

class ShadersBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Synchronizacja komend slash z Discordem
        await self.tree.sync()
        print("Komendy slash zostały zsynchronizowane!")

client = ShadersBot()

@client.event
async def on_ready():
    print(f"Zalogowano jako {client.user}!")

# --- 1. POWITANIA (WELCOME) & ZAPROSZENIA ---
@client.event
async def on_member_join(member: discord.Member):
    welcome_channel_id = 1561740336726937660
    invite_channel_id = 1566902544406421615

    # Kanał powitań
    welcome_channel = member.guild.get_channel(welcome_channel_id)
    if welcome_channel:
        embed = discord.Embed(
            title="<:welcome1:1567488704979669003> NOWY UŻYTKOWNIK",
            description=(
                f"<:welcome2:1564005582736728156> Witaj, {member.mention}! Miło że wpadłeś jesteś naszą **{member.guild.member_count}** osobą!\n"
                f"<:welcome2:1564005582736728156> Pobierz **najlepsze dodatki do fivem** właśnie tutaj!\n"
                f"<:welcome2:1564005582736728156> **Życzymy** miłego pobytu na **SHADERS PROJECT**"
            ),
            color=0x2b2d31
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1563292364414648471/1567487836457009162/welcome.jpg")
        await welcome_channel.send(embed=embed)

    # Kanał zaproszeń / vanity
    invite_channel = member.guild.get_channel(invite_channel_id)
    if invite_channel:
        invite_source = "discord.gg/shadersproject"
        vanity_uses = 0
        try:
            vanity = await member.guild.vanity_invite()
            if vanity:
                vanity_uses = vanity.uses
        except Exception:
            pass

        embed_inv = discord.Embed(
            title="<:welcome1:1567488704979669003> NOWE ZAPROSZENIE",
            description=(
                f"<:welcome2:1564005582736728156> Nowe dołączenie do **Serwera**.\n"
                f"<:welcome2:1564005582736728156> Użytkownik: {member.mention}\n"
                f"<:welcome2:1564005582736728156> Źródło: Własny link serwera (`{invite_source}`)\n"
                f"<:welcome2:1564005582736728156> Łącznie użyć vanity: `{vanity_uses}`"
            ),
            color=0x2b2d31
        )
        embed_inv.set_image(url="https://cdn.discordapp.com/attachments/1563292364414648471/1567487781641527316/zaproszenie.jpg")
        await invite_channel.send(embed=embed_inv)

# --- 2. BOOSTY ---
@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    boost_channel_id = 1563296339847282771
    if not before.premium_since and after.premium_since:
        boost_channel = after.guild.get_channel(boost_channel_id)
        if boost_channel:
            embed = discord.Embed(
                title="<:boost1:1567489688032256041> New server Boost!",
                description=(
                    f"{after.mention} **BOOST!**\n"
                    f"*thanks for boosting our server!*\n"
                    f"*Go check out our booster zone!*\n\n"
                    f"<:boost2:1567489885365997638> **Boost level**\n"
                    f"<:boost3:1567490142908719155> Server Boost level: `{after.guild.premium_tier}`\n"
                    f"<:boost4:1567490339907043388> Boost count: `{after.guild.premium_subscription_count}`"
                ),
                color=0xf47fff
            )
            embed.set_thumbnail(url=after.display_avatar.url)
            embed.set_image(url="https://cdn.discordapp.com/attachments/1563292364414648471/1567487836897415209/boost.jpg")
            embed.set_footer(text="SHADERS PROJECT")
            await boost_channel.send(embed=embed)

# --- 3. LEGIT CHECK (Automatyczne czyszczenie i odświeżanie) ---
@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    
    legit_channel_id = 1566908229081108620
    if message.channel.id == legit_channel_id:
        try:
            async for m in message.channel.history(limit=10):
                if m.author == client.user:
                    await m.delete()
        except Exception:
            pass

        legit_embed = discord.Embed(
            title="☑️ JAK WYSTAWIĆ LEGIT CHECK",
            description=(
                "[☑️] Kupowałeś coś u nas? Wystaw legit check i wesprzyj renomę serwera!\n"
                "[ℹ️] Skopiuj poniższy format, uzupełnij dane i wyślij na tym kanale.\n\n"
                "📋 **WYMAGANY WZÓR**\n"
                "```+rep @osoba opis transakcji | kwota PLN | metoda```\n\n"
                "☑️ **PRZYKŁAD**\n"
                "```+rep @sprzedawca Bulletki | 30 PLN | BLIK```"
            ),
            color=0x2b2d31
        )
        legit_embed.set_image(url="https://cdn.discordapp.com/attachments/1563292364414648471/1567487784665616384/legit_check.jpg")
        legit_embed.set_footer(text="© SHADERS PROJECT - Zweryfikowane opinie")
        await message.channel.send(embed=legit_embed)
    
    await client.process_commands(message)

# --- WIDOKI PRZYCISKÓW I MENU ---

class InfoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Regulamin", style=discord.ButtonStyle.secondary, custom_id="btn_regulamin")
    async def regulamin_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        reg_embed = discord.Embed(
            title="# REGULAMIN SERWERA SHADERS PROJECT",
            description=(
                "- Traktuj wszystkich z szacunkiem. Hejt, nękanie i dyskryminacja są zabronione.\n"
                "- Zachowuj kulturę wypowiedzi. Dbamy o przyjazną atmosferę, więc choć przeklinanie jest dozwolone, prosimy, by nie było nadmierne.\n"
                "- Nie promuj innych serwerów, projektów ani usług bez zgody administracji. Nieautoryzowana reklama i spam mogą skutkować ostrzeżeniem, banem lub dodaniem na blacklistę.\n"
                "- Nie publikuj treści NSFW (materiałów pornograficznych, szokujących czy nieodpowiednich dla społeczności).\n"
                "- Nie udostępniaj danych osobowych na publicznych kanałach – takich jak adresy, numery telefonu, e-maile, PESEL i podobne.\n\n"
                "Administracja może reagować na łamanie zasad. W razie pytań zgłoś się na <#1561742350986903702>."
            ),
            color=0x2b2d31
        )
        await interaction.response.send_message(embed=reg_embed, ephemeral=True)

    @discord.ui.button(label="Info Partner", style=discord.ButtonStyle.secondary, custom_id="btn_partner")
    async def partner_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        partner_embed = discord.Embed(
            title="# WYMAGANIA PARTNERSTWA",
            description="- 300 osob na serwerze\n- nie może to być shop",
            color=0x2b2d31
        )
        await interaction.response.send_message(embed=partner_embed, ephemeral=True)


class RekrutacjaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Media", style=discord.ButtonStyle.primary, custom_id="rekru_media")
    async def media_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "media", 1567494614322122832)

    @discord.ui.button(label="Administracja", style=discord.ButtonStyle.primary, custom_id="rekru_admin")
    async def admin_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "administracja", 1567494915745644636)

    async def create_ticket(self, interaction: discord.Interaction, t_type: str, cat_id: int):
        guild = interaction.guild
        category = guild.get_channel(cat_id)
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.get_role(1540495893399081061): discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.get_role(1540359821323149392): discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=f"{interaction.user.name}-{t_type}",
            category=category,
            overwrites=overwrites
        )
        await channel.send(f"Witaj {interaction.user.mention}! Twoje zgłoszenie ({t_type}) zostało otwarte.")
        await interaction.response.send_message(content=f"Utworzono kanał: {channel.mention}", ephemeral=True)


class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Owner", value="ticket_owner", emoji="👑", description="ticket with a matter for the owners"),
            discord.SelectOption(label="Shop", value="ticket_shop", emoji="🛒", description="Ticket for purchase an item from our store"),
            discord.SelectOption(label="Support", value="ticket_support", emoji="❓", description="Support ticket for help in our server"),
            discord.SelectOption(label="Partner", value="ticket_partner", emoji="🤝", description="Ticket for partnership")
        ]
        super().__init__(placeholder="Select category", min_values=1, max_values=1, options=options, custom_id="select_ticket")

    async def callback(self, interaction: discord.Interaction):
        val = self.values[0]
        guild = interaction.guild
        
        cat_map = {
            "ticket_owner": (1567496735360811049, [1540359821323149392, 1540495893399081061]),
            "ticket_shop": (1567497043134386226, [1540359821323149392, 1540495893399081061]),
            "ticket_support": (1567497448379645984, []),
            "ticket_partner": (1567497662406725673, [])
        }

        cat_id, role_ids = cat_map.get(val, (None, []))
        category = guild.get_channel(cat_id)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        for r_id in role_ids:
            role = guild.get_role(r_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )
        await channel.send(f"Witaj {interaction.user.mention}! Opisz swoją sprawę, administracja zaraz odpowie.")
        await interaction.response.send_message(content=f"Utworzono ticket: {channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


# --- KOMENDY SLASH ---

@client.tree.command(name="info", description="Wysyła panel informacyjny")
async def info_cmd(interaction: discord.Interaction):
    if interaction.channel_id != 1561758533446410251:
        return await interaction.response.send_message("Tę komendę można użyć tylko na kanale administracyjnym!", ephemeral=True)
    
    target_channel = interaction.guild.get_channel(1563293981872488479)
    embed = discord.Embed(
        title="ℹ️ INFORMACJE",
        description=(
            "📖 **Regulamin serwera** kliknij przycisk **Regulamin**, żeby go zobaczyć\n"
            "⚙️ **Info Partner** kliknij przycisk **Info Partner**, żeby zobaczyć wymagania partnerstwa"
        ),
        color=0x2b2d31
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1563292364414648471/1567487837324968017/ticket.jpg")
    await target_channel.send(embed=embed, view=InfoView())
    await interaction.response.send_message("Wysłano panel informacyjny!", ephemeral=True)

@client.tree.command(name="rekrutacja", description="Wysyła panel rekrutacji")
async def rekrutacja_cmd(interaction: discord.Interaction):
    if interaction.channel_id != 1561758533446410251:
        return await interaction.response.send_message("Tę komendę można użyć tylko na kanale administracyjnym!", ephemeral=True)

    target_channel = interaction.guild.get_channel(1566906802094735481)
    embed = discord.Embed(
        title="# REKRUTACJA",
        description=(
            "# MEDIA\nwymagania:\n- aktywne konto tik tok\n- regulacja w stawianiu filmikow promujących serwer\n\n"
            "# ADMINISTRACJA\nwymagania:\n- promowanie serwera\n- udzielanie pomocy użytkownikom serwera"
        ),
        color=0x2b2d31
    )
    await target_channel.send(embed=embed, view=RekrutacjaView())
    await interaction.response.send_message("Wysłano panel rekrutacji!", ephemeral=True)

@client.tree.command(name="ticket", description="Wysyła panel ticketów")
async def ticket_cmd(interaction: discord.Interaction):
    if interaction.channel_id != 1561758533446410251:
        return await interaction.response.send_message("Tę komendę można użyć tylko na kanale administracyjnym!", ephemeral=True)

    target_channel = interaction.guild.get_channel(1561742350986903702)
    embed = discord.Embed(
        title="Tickets",
        description=(
            "**Ticket Owner**\n*Open if you have a demand to the owners*\n\n"
            "**Ticket Shop**\n*open if you you want to buy something*\n\n"
            "**Ticket Support**\n*Open if you need any help*\n\n"
            "**Ticket Partner**\n*Open if you want to collaborate with us*"
        ),
        color=0x2b2d31
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1563292364414648471/1567487837324968017/ticket.jpg")
    await target_channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("Wysłano panel ticketów!", ephemeral=True)

@client.tree.command(name="legit", description="Wysyła instrukcję Legit Check")
async def legit_cmd(interaction: discord.Interaction):
    if interaction.channel_id != 1561758533446410251:
        return await interaction.response.send_message("Tę komendę można użyć tylko na kanale administracyjnym!", ephemeral=True)

    target_channel = interaction.guild.get_channel(1566908229081108620)
    embed = discord.Embed(
        title="☑️ JAK WYSTAWIĆ LEGIT CHECK",
        description=(
            "[☑️] Kupowałeś coś u nas? Wystaw legit check i wesprzyj renomę serwera!\n"
            "[ℹ️] Skopiuj poniższy format, uzupełnij dane i wyślij na tym kanale.\n\n"
            "📋 **WYMAGANY WZÓR**\n"
            "```+rep @osoba opis transakcji | kwota PLN | metoda```\n\n"
            "☑️ **PRZYKŁAD**\n"
            "```+rep @sprzedawca Bulletki | 30 PLN | BLIK```"
        ),
        color=0x2b2d31
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1563292364414648471/1567487784665616384/legit_check.jpg")
    await target_channel.send(embed=embed)
    await interaction.response.send_message("Wysłano Legit Check!", ephemeral=True)

@client.tree.command(name="accept", description="Akceptuje podanie gracza")
@app_commands.describe(gracz="Oznaczenie gracza")
async def accept_cmd(interaction: discord.Interaction, gracz: discord.Member):
    result_channel = interaction.guild.get_channel(1566906866691473498)
    embed = discord.Embed(
        title="ℹ️ PODANIE",
        description=f"👤 {gracz.mention}\n📖 Twoje podanie zostało **zaakceptowane**!",
        color=0x43b581
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1563292364414648471/1567487783612719115/akcept.jpg")
    
    if result_channel:
        await result_channel.send(embed=embed)
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("Podanie zaakceptowane!", ephemeral=True)

@client.tree.command(name="odrzucone", description="Odrzuca podanie gracza")
@app_commands.describe(gracz="Oznaczenie gracza")
async def odrzucone_cmd(interaction: discord.Interaction, gracz: discord.Member):
    result_channel = interaction.guild.get_channel(1566906866691473498)
    embed = discord.Embed(
        title="ℹ️ PODANIE",
        description=f"👤 {gracz.mention}\n📖 Twoje podanie zostało **odrzucone**.",
        color=0xf04747
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1563292364414648471/1567487784099516466/odrzucone.jpg")
    
    if result_channel:
        await result_channel.send(embed=embed)
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("Podanie odrzucone!", ephemeral=True)

@client.tree.command(name="bandc", description="Banuje użytkownika z powiadomieniem")
@app_commands.describe(gracz="Użytkownik do zbanowania", powod="Powód bana")
async def bandc_cmd(interaction: discord.Interaction, gracz: discord.Member, powod: str):
    embed = discord.Embed(
        title="🔨 User has been banned for life",
        description=(
            f"👤 **User**: {gracz.mention}\n"
            f"🆔 **ID**: `{gracz.id}`\n"
            f"🛡️ **Administrator**: {interaction.user.mention}\n"
            f"📝 **Reason**:\n```{powod}```"
        ),
        color=0xff0000
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1563292364414648471/1567487782325067896/ban.jpg")
    
    await gracz.ban(reason=powod)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="unbandc", description="Odbanowuje użytkownika")
@app_commands.describe(id="ID użytkownika")
async def unbandc_cmd(interaction: discord.Interaction, id: str):
    user_id = int(id)
    user = await client.fetch_user(user_id)
    await interaction.guild.unban(user)

    embed = discord.Embed(
        title="🔓 User has been unbanned",
        description=(
            f"🆔 **ID**: `{user_id}`\n"
            f"🛡️ **Administrator**: {interaction.user.mention}"
        ),
        color=0x43b581
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1563292364414648471/1567487782757204009/unban.jpg")
    await interaction.response.send_message(embed=embed)

client.run(os.getenv("DISCORD_TOKEN"))