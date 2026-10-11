# Cooldown dynamiczny resetujący się o północy
class MidnightCooldown:
    def __call__(self, interaction: discord.Interaction):
        now = datetime.now(timezone.utc)
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0, 0), tzinfo=timezone.utc)
        delta_seconds = int((tomorrow - now).total_seconds())
        
        # Tworzymy bucket na podstawie ID użytkownika z czasem wygasającym o północy
        bucket = commands.CooldownMapping.from_cooldown(1, delta_seconds, commands.BucketType.user)
        retry_after = bucket.update_rate_limit(interaction)
        if retry_after:
            raise discord.app_commands.CommandOnCooldown(bucket, retry_after, commands.BucketType.user)
        return True

midnight_cd = MidnightCooldown()

@bot.tree.command(name="minigame", description="Losowanie nagrody w Cold Cfg")
async def minigame(interaction: discord.Interaction):
    # Sprawdzamy i aktualizujemy cooldown o północy
    try:
        midnight_cd(interaction)
    except discord.app_commands.CommandOnCooldown as error:
        hours = int(error.retry_after // 3600)
        minutes = int((error.retry_after % 3600) // 60)
        return await interaction.response.send_message(
            f"⏳ Możesz zagrać ponownie dopiero po północy! Spróbuj za ok. {hours}h {minutes}m.",
            ephemeral=True
        )

    import random
    won = random.choice([False, False, True]) # Szansa na wygraną

    if won:
        role = interaction.guild.get_role(WINNER_ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
        
        embed = discord.Embed(
            title="🎉 Gratulacje! Wygrana!",
            description=(
                f"<@!{interaction.user.id}>, udało Ci się wygrać w minigrze!\n"
                f"Otrzymałeś specjalną rangę nagrody!\n\n"
                f"*Wpadnij ponownie po północy na kolejne losowanie!*"
            ),
            color=0x2ecc71
        )
    else:
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
    embed.set_image(url=MINIGAME_IMAGE_URL)
    await interaction.response.send_message(embed=embed)