import os
import discord
from discord.ext import commands

# --- KONFIGURACJA BRANDINGU POLISHCFG ---
EMBED_COLOR = 0x2B2D31
BRAND_ICON_URL = "https://cdn.discordapp.com/attachments/1200000000000000000/1200000000000000000/polishcfg_logo.png"
FOOTER_TEXT = "POLISHCFG • Wszelkie prawa zastrzeżone"

# ID Kanałów i Ról (Zastąp własnymi ID, jeśli są inne!)
VERIFY_CHANNEL_ID = 123456789012345678
TICKET_CHANNEL_ID = 123456789012345679
VERIFIED_ROLE_ID = 123456789012345680

class PolishBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        print("Czyszczenie i synchronizacja komend slash...")
        await self.tree.sync()
        print("Komendy slash zsynchronizowane!")

bot = PolishBot()

# --- PANEL WERYFIKACJI ---
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.green, custom_id="verify_btn", emoji="✅")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(VERIFIED_ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Pomyślnie zweryfikowano! Uzyskano dostęp do serwera POLISHCFG.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Błąd: Nie znaleziono roli weryfikacyjnej na serwerze.", ephemeral=True)

# --- PANEL TICKETÓW ---
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Otwórz Ticket", style=discord.ButtonStyle.blurple, custom_id="ticket_btn", emoji="📩")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel_name = f"ticket-{interaction.user.name}"
        ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
        
        ticket_description = f"Witaj {interaction.user.mention}!\nOpisz swój problem, a nasza obsługa odpowie najszybciej jak to możliwe."
        
        embed = discord.Embed(
            title="POLISHCFG • Pomoc i Wsparcie",
            description=ticket_description,
            color=EMBED_COLOR
        )
        embed.set_thumbnail(url=BRAND_ICON_URL)
        embed.set_footer(text=FOOTER_TEXT)
        
        await ticket_channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Utworzono Twój ticket: {ticket_channel.mention}", ephemeral=True)

# --- KOMENDY SLASH ---
@bot.tree.command(name="setup_weryfikacja", description="Wysyła panel weryfikacyjny POLISHCFG")
async def setup_weryfikacja(interaction: discord.Interaction):
    channel = bot.get_channel(VERIFY_CHANNEL_ID) or interaction.channel
    embed = discord.Embed(
        title="POLISHCFG • Weryfikacja",
        description="Kliknij poniższy przycisk, aby zweryfikować swoje konto i uzyskać pełen dostęp do serwera.",
        color=EMBED_COLOR
    )
    embed.set_thumbnail(url=BRAND_ICON_URL)
    embed.set_footer(text=FOOTER_TEXT)
    
    await channel.send(embed=embed, view=VerifyView())
    await interaction.response.send_message("✅ Panel weryfikacji został wysłany!", ephemeral=True)

@bot.tree.command(name="setup_tickets", description="Wysyła panel pomocy ticket POLISHCFG")
async def setup_tickets(interaction: discord.Interaction):
    channel = bot.get_channel(TICKET_CHANNEL_ID) or interaction.channel
    embed = discord.Embed(
        title="POLISHCFG • Centrum Pomocy",
        description="Potrzebujesz pomocy lub masz pytanie odnośnie naszych konfiguracji?\nKliknij poniżej, aby otworzyć zgłoszenie.",
        color=EMBED_COLOR
    )
    embed.set_thumbnail(url=BRAND_ICON_URL)
    embed.set_footer(text=FOOTER_TEXT)
    
    await channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("✅ Panel ticketów został wysłany!", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user.name}!")
    bot.add_view(VerifyView())
    bot.add_view(TicketView())

token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("BŁĄD: Brak wartości DISCORD_TOKEN w zmiennych środowiskowych!")