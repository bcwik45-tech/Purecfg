import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- 1. WERYFIKACJA ---
class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_name = ".gg/purecfg"
        role = discord.utils.get(interaction.guild.roles, name=role_name)

        if not role:
            await interaction.response.send_message(f"Błąd: Nie znaleziono roli '{role_name}' na serwerze!", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.response.send_message("Masz już zweryfikowane konto!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Pomyślnie zweryfikowano konto! Witaj na serwerze.", ephemeral=True)

# --- 2. ZAMYKANIE TICKETA ---
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket_button")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Zamykanie ticketa za 3 sekundy...", ephemeral=True)
        await asyncio.sleep(3)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"❌ BŁĄD USUWANIA KANAŁU: {e}")

# --- 3. TICKETY I KATEGORIE ---
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        guild = interaction.guild
        member = interaction.user

        # Nowe, zaktualizowane ID kategorii
        category_ids = {
            "owner": 1556300080355606608,
            "shop": 1556300130892906506,
            "support": 1556300180624769105,
            "recruitment": 1556300236526329936
        }

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        allowed_roles = []
        if ticket_type == "owner":
            allowed_roles = ["Owner", "Co-Owner"]
            title_text = "👑 Owner Ticket"
            desc_text = "Hello! Welcome to the Owner contact.\n**Please state your case clearly** and wait for the owner/co-owner.\n\nTo close the ticket, click the button below."
        elif ticket_type == "support":
            allowed_roles = ["Trial Staff", "Staff", "Head Staff", "Co-Owner", "Owner"]
            title_text = "❓ Support Ticket"
            desc_text = "Hello! Welcome to Support.\n**What do you need help with?** Please describe your issue and wait for the staff.\n\nTo close the ticket, click the button below."
        elif ticket_type == "shop":
            allowed_roles = ["Owner", "Co-Owner"]
            title_text = "🛒 Shop Ticket"
            desc_text = "Hello! Welcome to the Shop.\n**What would you like to buy today?** Please specify your order and wait for the staff.\n\nTo close the ticket, click the button below."
        elif ticket_type == "recruitment":
            allowed_roles = ["Owner", "Co-Owner", "Staff", "Head Staff"]
            title_text = "📄 Recruitment Ticket"
            desc_text = "Hello! Welcome to Recruitment.\n**Please provide your application details** and wait for the review.\n\nTo close the ticket, click the button below."

        role_mentions = []
        for r_name in allowed_roles:
            role = discord.utils.get(guild.roles, name=r_name)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
                role_mentions.append(role.mention)

        channel_name = f"ticket-{ticket_type}-{member.name}".lower()
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)

        if existing_channel:
            await interaction.response.send_message(f"Masz już otwarty ticket: {existing_channel.mention}", ephemeral=True)
            return

        # Pobieranie kategorii bezpośrednio przez API Discorda po ID
        category = None
        cat_id = category_ids.get(ticket_type)
        if cat_id:
            try:
                category = await guild.fetch_channel(cat_id)
            except Exception as e:
                print(f"❌ Nie udało się pobrać kategorii po ID {cat_id}: {e}")

        ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, category=category)
        
        await interaction.response.send_message(f"✅ Utworzono dla Ciebie ticket: {ticket_channel.mention}", ephemeral=True)

        pings = f"{member.mention}"
        if role_mentions:
            pings += " " + " ".join(role_mentions)

        embed = discord.Embed(
            title=title_text,
            description=desc_text,
            color=discord.Color.red()
        )

        await ticket_channel.send(content=f"Hello {pings}!", embed=embed, view=CloseTicketView())

    @discord.ui.button(label="Shop", style=discord.ButtonStyle.green, emoji="🛒", custom_id="ticket_shop")
    async def shop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "shop")

    @discord.ui.button(label="Owner", style=discord.ButtonStyle.grey, emoji="👑", custom_id="ticket_owner")
    async def owner_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "owner")

    @discord.ui.button(label="Support", style=discord.ButtonStyle.blurple, emoji="❓", custom_id="ticket_support")
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "support")

    @discord.ui.button(label="Recruitment", style=discord.ButtonStyle.red, emoji="📄", custom_id="ticket_recruitment")
    async def recruitment_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "recruitment")

@bot.event
async def on_ready():
    bot.add_view(VerificationView())
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
    print(f"Zalogowano jako {bot.user}!")

# --- 4. AUTOMATYCZNE POWITANIA ---
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="wlc")
    if channel:
        member_count = member.guild.member_count
        created_at_str = member.created_at.strftime("%d.%m.%Y %H:%M:%S")
        joined_at_str = member.joined_at.strftime("%d %B %Y %H:%M") if member.joined_at else "Teraz"

        embed = discord.Embed(title="New member!", color=discord.Color.dark_theme())
        embed.description = (
            f"🎉 Hi {member.mention}\n"
            f"Welcome to the best cfg in Poland!\n"
            f"Go check out our stuff!\n"
            f"**You're our {member_count} member!**\n\n"
            f"**Member Info:**\n"
            f"🪪 **Discord account created:** {created_at_str}\n"
            f"👤 **Username:** `{member.name}`\n"
            f"📅 **Joined at:** {joined_at_str}"
        )
        embed.set_thumbnail(url="https://i.imgur.com/7Y1p3FH.png") 

        await channel.send(embed=embed)

# --- 5. KOMENDA !SAY ---
@bot.command()
async def say(ctx, *, wiadomosc: str):
    await ctx.message.delete()
    await ctx.send(wiadomosc)

# --- 6. KOMENDY SETUPUJĄCE ---
@bot.command()
async def setup_weryfikacja(ctx):
    embed = discord.Embed(
        title="Verification",
        description="Click on verification to get access to the channels",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=VerificationView())

@bot.command(aliases=["set_tickets"])
async def setup_tickets(ctx):
    embed = discord.Embed(
        title="Tickets",
        description="Want to place an order, need to contact the owner or staff for help?\nClick the appropriate button below to open a private channel with the administration.\n\nPlease don't open the tickets without a proper reason.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed, view=TicketView())

# --- URUCHOMIENIE BOTA ---
bot.run(os.getenv("DISCORD_TOKEN"))