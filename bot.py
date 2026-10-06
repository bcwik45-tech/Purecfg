import os
import discord
from discord import app_commands
from discord.ext import commands
import io
from datetime import datetime, timezone

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

minigame_cooldowns = {}

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_button")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        channel = interaction.channel
        
        messages_history = []
        async for msg in channel.history(limit=500, oldest_first=True):
            timestamp = msg.created_at.strftime('%Y-%m-%d %H:%M')
            messages_history.append(f"[{timestamp}] {msg.author}: {msg.content}")
        
        transcript_text = f"Transcript z ticketa: {channel.name}\n" + "\n".join(messages_history)
        file = discord.File(io.BytesIO(transcript_text.encode('utf-8')), filename=f"transcript-{channel.name}.txt")
        
        try:
            await interaction.user.send("Oto transcript z Twojego zamkniętego ticketa:", file=file)
        except Exception:
            pass

        await interaction.followup.send("🔒 Zamykanie kanału...", ephemeral=True)
        await channel.delete()

    @discord.ui.button(label="Call Staff 🔔", style=discord.ButtonStyle.secondary, custom_id="call_staff_button")
    async def call_staff(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        channel = interaction.channel
        guild = interaction.guild
        category = channel.category

        roles_to_ping = []
        targets_to_check = list(channel.overwrites.items())
        if category:
            targets_to_check.extend(list(category.overwrites.items()))

        for target, overwrite in targets_to_check:
            if isinstance(target, discord.Role) and target != guild.default_role and target != guild.me:
                if overwrite.view_channel is True and target.mention not in roles_to_ping:
                    roles_to_ping.append(target.mention)

        if roles_to_ping:
            ping_str = " ".join(roles_to_ping)
            await channel.send(f"🔔 {interaction.user.mention} wzywa administrację: {ping_str}")
            await interaction.followup.send("✅ Wezwano staffa do ticketa!", ephemeral=True)
        else:
            await interaction.followup.send("❌ Nie znaleziono ról z dostępem do tego kanału, które można spingować.", ephemeral=True)

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj", style=discord.ButtonStyle.green, custom_id="purecfg_verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Zostałeś pomyślnie zweryfikowany!", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket_channel(self, interaction: discord.Interaction, ticket_type: str, emoji: str, title_name: str, desc_text: str, category_id: int = None):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        
        category = None
        if category_id:
            category = guild.get_channel(category_id)
        
        if not category:
            for cat in guild.categories:
                if ticket_type.lower() in cat.name.lower() or ticket_type in cat.name.lower():
                    category = cat
                    break
                    
        if not category:
            category = interaction.channel.category

        try:
            channel = await guild.create_text_channel(
                f"{emoji}-{ticket_type}-{interaction.user.name}", 
                overwrites=overwrites,
                category=category
            )
            
            roles_to_ping = []
            targets_to_check = list(channel.overwrites.items())
            if category:
                targets_to_check.extend(list(category.overwrites.items()))

            for target, overwrite in targets_to_check:
                if isinstance(target, discord.Role) and target != guild.default_role and target != guild.me:
                    if overwrite.view_channel is True and target.mention not in roles_to_ping:
                        roles_to_ping.append(target.mention)

            ping_str = " ".join(roles_to_ping) if roles_to_ping else ""

            await interaction.followup.send(f"✅ Utworzono Twój ticket: {channel.mention}", ephemeral=True)
            
            embed = discord.Embed(
                title=title_name,
                description=desc_text,
                color=discord.Color.from_rgb(47, 49, 54)
            )
            
            content_msg = f"Hello {interaction.user.mention}!"
            if ping_str:
                content_msg += f" {ping_str}"

            await channel.send(content_msg, embed=embed, view=CloseTicketView())
            
        except Exception as e:
            await interaction.followup.send(f"❌ Nie udało się utworzyć kanału ticketu: {e}", ephemeral=True)

    @discord.ui.button(label="Shop 🛒", style=discord.ButtonStyle.green, custom_id="ticket_shop")
    async def shop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "shop", "🛒", "Shop Ticket", "Hello! Welcome to the Shop.\n**What would you like to buy today?** Please specify your order and wait for the staff.\n\nTo close the ticket, click the button below.", category_id=1556300130892906506)

    @discord.ui.button(label="Owner 👑", style=discord.ButtonStyle.secondary, custom_id="ticket_owner")
    async def owner_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "owner", "👑", "Owner Ticket", "Hello! Welcome to the Owner contact.\n**How can the owner help you?** Please describe your case and wait for a response.\n\nTo close the ticket, click the button below.")

    @discord.ui.button(label="Support ❓", style=discord.ButtonStyle.primary, custom_id="ticket_support")
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "support", "❓", "Support Ticket", "Hello! Welcome to Support.\n**What issue are you experiencing?** Describe it clearly and wait for the staff.\n\nTo close the ticket, click the button below.")

    @discord.ui.button(label="Recruitment 📄", style=discord.ButtonStyle.danger, custom_id="ticket_recruitment")
    async def recruitment_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "recruitment", "📄", "Recruitment Ticket", "Hello! Welcome to Recruitment.\n**Want to join the staff?** Provide your details and experience below.\n\nTo close the ticket, click the button below.")

class PartnerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Partner 🤝", style=discord.ButtonStyle.primary, custom_id="purecfg_partner_button")
    async def partner_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        category = None
        for cat in guild.categories:
            if "partner" in cat.name.lower():
                category = cat
                break
        if not category:
            category = interaction.channel.category
        
        try:
            channel = await guild.create_text_channel(f"partner-{interaction.user.name}", overwrites=overwrites, category=category)
            
            roles_to_ping = []
            targets_to_check = list(channel.overwrites.items())
            if category:
                targets_to_check.extend(list(category.overwrites.items()))

            for target, overwrite in targets_to_check:
                if isinstance(target, discord.Role) and target != guild.default_role and target != guild.me:
                    if overwrite.view_channel is True and target.mention not in roles_to_ping:
                        roles_to_ping.append(target.mention)
            ping_str = " ".join(roles_to_ping) if roles_to_ping else ""

            await interaction.followup.send(f"✅ Utworzono kanał partnerstwa: {channel.mention}", ephemeral=True)
            
            embed = discord.Embed(
                title="Partnership Ticket",
                description="Hello! Welcome to Partnership.\n**Please provide your server invite and details.**\n\nTo close the ticket, click the button below.",
                color=discord.Color.gold()
            )
            content_msg = f"Hello {interaction.user.mention}!"
            if ping_str:
                content_msg += f" {ping_str}"

            await channel.send(content_msg, embed=embed, view=CloseTicketView())
        except Exception as e:
            await interaction.followup.send(f"❌ Wystąpił błąd: {e}", ephemeral=True)

class PurecfgBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(VerifyView())
        self.add_view(TicketView())
        self.add_view(PartnerView())
        self.add_view(CloseTicketView())

        GUILD_ID = discord.Object(id=1540347771616362638)
        self.tree.copy_global_to(guild=GUILD_ID)
        await self.tree.sync(guild=GUILD_ID)
        print("Zsynchronizowano komendy i widoki dla serwera!")

bot = PurecfgBot()

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_member_join(member: