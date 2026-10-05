import os
import discord
from discord import app_commands
from discord.ext import commands

# Konfiguracja intencji bota
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Zostałeś pomyślnie zweryfikowany!", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Stwórz Ticket 🎫", style=discord.ButtonStyle.blurple, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        # Tworzy prywatny kanał dla użytkownika
        channel = await guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        await interaction.response.send_message(f"✅ Utworzono Twój ticket: {channel.mention}", ephemeral=True)
        await channel.send(f"Witaj {interaction.user.mention}! Opisz swój problem, a administracja wkrótce odpowie.")

class PurecfgBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Rejestracja widoków na stałe
        self.add_view(VerifyView())
        self.add_view(TicketView())

        # Synchronizacja komend dla Twojego serwera
        GUILD_ID = discord.Object(id=1540347771616362638)
        self.tree.copy_global_to(guild=GUILD_ID)
        await self.tree.sync(guild=GUILD_ID)
        print(f"Zsynchronizowano natychmiast komendy dla serwera!")

bot = PurecfgBot()

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user} (ID: {bot.user.id})")
    print("Bot jest gotowy do działania!")

# Komenda /setup_verify
@bot.tree.command(name="setup_verify", description="Wysyła panel weryfikacji na obecny kanał")
async def setup_verify(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Brak uprawnień administratora!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="Verification",
        description="Click on verification to get access to the channels",
        color=discord.Color.green()
    )
    await interaction.channel.send(embed=embed, view=VerifyView())
    await interaction.response.send_message("✅ Wysłano panel weryfikacji!", ephemeral=True)

# Komenda /setup_ticket
@bot.tree.command(name="setup_ticket", description="Wysyła panel tworzenia ticketów")
async def setup_ticket(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Brak uprawnień administratora!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="Centrum Pomocy - Tickety",
        description="Kliknij przycisk poniżej, aby utworzyć prywatny kanał zgłoszeniowy z administracją.",
        color=discord.Color.blue()
    )
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("✅ Wysłano panel ticketów!", ephemeral=True)

# Komenda /minigame
@bot.tree.command(name="minigame", description="Rozpocznij minigrę (dostępne tylko na kanale #minigame)")
async def minigame(interaction: discord.Interaction):
    if interaction.channel.name != "minigame":
        await interaction.response.send_message("❌ Tej komendy można używać tylko na kanale #minigame!", ephemeral=True)
        return
    await interaction.response.send_message("🎮 Rozpoczęto minigrę! Powodzenia!")

# Komenda /wzor_staff
@bot.tree.command(name="wzor_staff", description="Wyświetla wzór podania na staff")
async def wzor_staff(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📝 Rekrutacja na Staff - Wzór",
        description="Skopiuj poniższy wzór i wyślij go w odpowiednim kanale rekrutacyjnym.",
        color=discord.Color.blue()
    )
    embed.add_field(name="1. Twoje imię:", value="[Wpisz tutaj]", inline=False)
    embed.add_field(name="2. Twój wiek:", value="[Wpisz tutaj]", inline=False)
    embed.add_field(name="3. Doświadczenie:", value="[Wpisz tutaj]", inline=False)
    await interaction.response.send_message(embed=embed)

# Komenda /accept
@bot.tree.command(name="accept", description="Akceptuje kandydata i nadaje rangę Trial Staff")
@app_commands.describe(member="Użytkownik, którego chcesz zaakceptować")
async def accept(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Nie masz uprawnień, aby użyć tej komendy.", ephemeral=True)
        return

    role_id = 1540360086617063584
    role = interaction.guild.get_role(role_id)
    
    if not role:
        await interaction.response.send_message("❌ Nie znaleziono roli o podanym ID na tym serwerze!", ephemeral=True)
        return

    try:
        await member.add_roles(role)
        await interaction.response.send_message(f"✅ Pomyślnie zaakceptowano użytkownika {member.mention} i nadano rangę **{role.name}**!")
    except Exception as e:
        await interaction.response.send_message(f"❌ Wystąpił błąd podczas nadawania roli: {e}", ephemeral=True)

# Uruchomienie bota
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("BŁĄD: Nie znaleziono zmiennej środowiskowej DISCORD_TOKEN!")