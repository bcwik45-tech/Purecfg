@bot.tree.command(name="rolaall", description="Nadaje rolę wszystkim użytkownikom na serwerze, którzy jej nie mają")
async def rolaall(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Nie masz uprawnień administratora!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    ROLE_ID = 1540360249775493230
    role = interaction.guild.get_role(ROLE_ID)

    if not role:
        await interaction.followup.send("❌ Nie znaleziono roli o podanym ID na serwerze!", ephemeral=True)
        return

    success_count = 0
    already_has_count = 0
    error_count = 0

    # Upewnij się, że masz pobranych członków (intents.members jest włączone)
    for member in interaction.guild.members:
        if role in member.roles:
            already_has_count += 1
            continue
        try:
            await member.add_roles(role)
            success_count += 1
        except Exception:
            error_count += 1

    await interaction.followup.send(
        f"✅ Zakończono proces nadawania roli!\n"
        f"👤 Nadano nowo: **{success_count}**\n"
        f"ℹ️ Już posiadali: **{already_has_count}**\n"
        f"❌ Błędy (np. brak uprawnień bota): **{error_count}**",
        ephemeral=True
    )