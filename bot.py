import os
import discord
from discord import app_commands
from discord.ext import commands

# Konfiguracja intencji bota
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

class PurecfgBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Zsynchronizowano komendy dla {self.user}")

bot = PurecfgBot()

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user} (ID: {bot.user.id})")
    print("Bot jest gotowy do działania!")

# Komenda /minigame (ograniczona do kanału #minigame)
@bot.tree.command(name="minigame", description="Rozpocznij minigrę (dostępne tylko na kanale #minigame)")
async def minigame(interaction: discord.Interaction):
    if interaction.channel.name != "minigame":
        await interaction.response.send_message("❌ Tej komendy można używać tylko na kanale #minigame!", ephemeral=True)
        return
    
    await interaction.response.send_message("🎮 Rozpoczęto minigrę! Powodzenia!")

# Komenda /wzor_staff (wzorzec rekrutacyjny)
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

# Komenda /accept (nadawanie roli Trial Staff - ID: 1540360086617063584)
@bot.tree.command(name="accept", description="Akceptuje kandydata i nadaje rangę Trial Staff")
@app_commands.describe(member="Użytkownik, którego chcesz zaakceptować")
async def accept(interaction: discord.Interaction, member: discord.Member):
    # Sprawdzenie uprawnień (np. administrator lub zarządzanie rolami)
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

# Uruchomienie bota przy użyciu tokena ze zmiennych środowiskowych
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("BŁĄD: Nie znaleziono zmiennej środowiskowej DISCORD_TOKEN!")