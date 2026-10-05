import os
import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj", style=discord.ButtonStyle.green, custom_id="purecfg_verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Zostałeś pomyślnie zweryfikowany!", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket_channel(self, interaction: discord.Interaction, ticket_type: str):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        try:
            channel = await guild.create_text_channel(f"{ticket_type}-{interaction.user.name}", overwrites=overwrites)
            await interaction.followup.send(f"✅ Utworzono Twój ticket: {channel.mention}", ephemeral=True)
            await channel.send(f"Witaj {interaction.user.mention}! Wybrałeś kategorię: **{ticket_type.upper()}**. Opisz swój sprawę, a administracja wkrótce odpowie.")
        except Exception as e:
            await interaction.followup.send(f"❌ Nie udało się utworzyć kanału ticketu: {e}", ephemeral=True)

    @discord.ui.button(label="Shop 🛒", style=discord.ButtonStyle.green, custom_id="ticket_shop")
    async def shop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "shop")

    @discord.ui.button(label="Owner 👑", style=discord.ButtonStyle.secondary, custom_id="ticket_owner")
    async def owner_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "owner")

    @discord.ui.button(label="Support ❓", style=discord.ButtonStyle.primary, custom_id="ticket_support")
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "support")

    @discord.ui.button(label="Recruitment 📄", style=discord.ButtonStyle.danger, custom_id="ticket_recruitment")
    async def recruitment_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "recruitment")

class PartnerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Partner 🤝", style=discord.ButtonStyle.blurple, custom_id="purecfg_partner_button") # discord.ui.button w odcieniu żółtym/primary/secondary (użyjemy żółtego jako blurple/secondary albo oznacznik)
    async def partner_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        try:
            channel = await guild.create_text_channel(f"partner-{interaction.user.name}", overwrites=overwrites)
            await interaction.followup.send(f"✅ Utworzono kanał partnerstwa: {channel.mention}", ephemeral=True)
            await channel.send(f"Witaj {interaction.user.mention}! Chcesz nawiązać współpracę? Przedstaw szczegóły.")
        except Exception as e:
            await interaction.followup.send(f"❌ Wystąpił błąd: {e}", ephemeral=True)

class PurecfgBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(VerifyView())
        self.add_view(TicketView())
        self.add_view(PartnerView())

        GUILD_ID = discord.Object(id=1540347771616362638)
        self.tree.copy_global_to(guild=GUILD_ID)
        await self.tree.sync(guild=GUILD_ID)
        print("Zsynchronizowano komendy i widoki dla serwera!")

bot = PurecfgBot()

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user} (ID: {bot.user.id})")

@bot.tree.command(name="setup_verify", description="Wysyła panel weryfikacji")
async def setup_verify(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Brak uprawnień!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="Verification",
        description="Click on verification to get access to the channels",
        color=discord.Color.green()
    )
    await interaction.channel.send(embed=embed, view=VerifyView())
    await interaction.response.send_message("✅ Wysłano panel weryfikacji!", ephemeral=True)

@bot.tree.command(name="setup_ticket", description="Wysyła oficjalny panel ticketów")
async def setup_ticket(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Brak uprawnień!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🎫 Tickets",
        description="Want to place an order, need to contact the owner or staff for help?\nClick the appropriate button below to open a private channel with the administration.\n\nPlease don't open the tickets without a proper reason.",
        color=discord.Color.from_rgb(47, 49, 54)
    )
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("✅ Wysłano panel ticketów!", ephemeral=True)

@bot.tree.command(name="setup_partner", description="Wysyła panel partnerstw z żółtym przyciskiem")
async def setup_partner(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Brak uprawnień!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🤝 Partnership / Współpraca",
        description="Chcesz nawiązać partnerstwo z naszym serwerem? Kliknij przycisk poniżej, aby otworzyć kanał zgłoszeniowy.",
        color=discord.Color.gold()
    )
    # Żółty przycisk uzyskujemy używając style.secondary lub blurple (w Discord API styl żółty to ButtonStyle.blurple lub secondary/success w zależności od preferencji, tutaj damy customowy)
    view = PartnerView()
    # Zmiana stylu przycisku na żółty (Secondary w Discord to szary, Primary to niebieski, Success to zielony, Danger to czerwony. Discord nie ma natywnego żółtego koloru jako pojedynczego enum dla zwykłego przycisku linku poza szarym/blurple, ale użyjemy blurple lub secondary w zależności od wyglądu, albo zrobimy szary/niebieski jako uniwersalny). 
    # Dla pewności ustawiamy styl secondary (szary/neutralny) lub przełączamy na blurple.
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Wysłano panel partnerstw!", ephemeral=True)

@bot.tree.command(name="minigame", description="Rozpocznij minigrę")
async def minigame(interaction: discord.Interaction):
    if interaction.channel.name != "minigame":
        await interaction.response.send_message("❌ Tej komendy można używać tylko na kanale #minigame!", ephemeral=True)
        return
    await interaction.response.send_message("🎮 Rozpoczęto minigrę! Powodzenia!")

@bot.tree.command(name="wzor_staff", description="Wyświetla wzór podania na staff")
async def wzor_staff(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📝 Rekrutacja na Staff - Wzór",
        description="Skopiuj poniższy wzór i wyślij go w odpowiednim kanale.",
        color=discord.Color.blue()
    )
    embed.add_field(name="1. Twoje imię:", value="[Wpisz tutaj]", inline=False)
    embed.add_field(name="2. Twój wiek:", value="[Wpisz tutaj]", inline=False)
    embed.add_field(name="3. Doświadczenie:", value="[Wpisz tutaj]", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="accept", description="Akceptuje kandydata i nadaje rangę Trial Staff")
@app_commands.describe(member="Użytkownik, którego chcesz zaakceptować")
async def accept(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Nie masz uprawnień.", ephemeral=True)
        return

    role = interaction.guild.get_role(1540360086617063584)
    if not role:
        await interaction.response.send_message("❌ Nie znaleziono roli Trial Staff!", ephemeral=True)
        return

    try:
        await member.add_roles(role)
        await interaction.response.send_message(f"✅ Zaakceptowano użytkownika {member.mention}!")
    except Exception as e:
        await interaction.response.send_message(f"❌ Błąd: {e}", ephemeral=True)

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)