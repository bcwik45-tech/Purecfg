const { 
    Client, 
    GatewayIntentBits, 
    EmbedBuilder, 
    SlashCommandBuilder, 
    ActionRowBuilder, 
    ButtonBuilder, 
    ButtonStyle, 
    REST, 
    Routes,
    PermissionFlagsBits,
    ChannelType
} = require('discord.js');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.GuildBans
    ]
});

// --- KONFIGURACJA ID ---
const WELCOME_CHANNEL_ID = '1556280506516115466'; // Kanał powitań
const BANNER_URL = 'https://i.imgur.com/YOUR_BANNER_HERE.png'; // Zmień na link do swojego głównego bannera

// Kategorie ticketów
const TICKET_CATEGORIES = {
    shop: '1556300130892906506',
    owner: '1556300080355606608',
    support: '1556300180624769105',
    recruitment: '1556300236526329936',
    partner: '1556383124424892606'
};

// Role mające dostęp do poszczególnych ticketów
const TICKET_ROLES = {
    shop: ['1540359821323149392'],
    owner: ['1540359821323149392', '1540495893399081061'],
    support: ['1540359821323149392', '1540495893399081061', '1556062543963750400', '1540359905175801946', '1540360086617063584'],
    recruitment: ['1540359821323149392', '1540495893399081061', '1556062543963750400', '1540359905175801946'],
    partner: ['1540359821323149392', '1540495893399081061']
};

// Role nadawane przez /accept
const ACCEPT_ROLES = ['1540359963346608168', '1540360086617063584'];

// Rejestracja komend Slash
const commands = [
    new SlashCommandBuilder()
        .setName('say')
        .setDescription('Wysyła wiadomość w imieniu bota')
        .addStringOption(option => option.setName('message').setDescription('Treść').setRequired(true)),
    new SlashCommandBuilder()
        .setName('bandc')
        .setDescription('Banuje użytkownika')
        .setDefaultMemberPermissions(PermissionFlagsBits.BanMembers)
        .addUserOption(option => option.setName('target').setDescription('Użytkownik').setRequired(true))
        .addStringOption(option => option.setName('reason').setDescription('Powód').setRequired(true)),
    new SlashCommandBuilder()
        .setName('unbandc')
        .setDescription('Odbanowuje użytkownika')
        .setDefaultMemberPermissions(PermissionFlagsBits.BanMembers)
        .addStringOption(option => option.setName('userid').setDescription('ID użytkownika').setRequired(true))
        .addStringOption(option => option.setName('reason').setDescription('Powód').setRequired(false)),
    new SlashCommandBuilder()
        .setName('minigame')
        .setDescription('Losowanie nagrody w grze Cold Cfg'),
    new SlashCommandBuilder()
        .setName('accept')
        .setDescription('Nadaje role zweryfikowanemu użytkownikowi')
        .setDefaultMemberPermissions(PermissionFlagsBits.ManageRoles)
        .addUserOption(option => option.setName('target').setDescription('Użytkownik').setRequired(true)),
    new SlashCommandBuilder()
        .setName('setup')
        .setDescription('Wysyła panele weryfikacji oraz ticketów')
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator)
].map(command => command.toJSON());

client.once('ready', async () => {
    console.log(`Zalogowano jako ${client.user.tag}!`);
    const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);
    try {
        await rest.put(Routes.applicationCommands(client.user.id), { body: commands });
        console.log('Zarejestrowano komendy slash.');
    } catch (e) {
        console.error(e);
    }
});

// --- POWITANIA (guildMemberAdd) ---
client.on('guildMemberAdd', async (member) => {
    const channel = member.guild.channels.cache.get(WELCOME_CHANNEL_ID);
    if (!channel) return;

    const createdAt = `<t:${Math.floor(member.user.createdTimestamp / 1000)}:d> <t:${Math.floor(member.user.createdTimestamp / 1000)}:T>`;
    const joinedAt = `<t:${Math.floor(member.joinedTimestamp / 1000)}:d> <t:${Math.floor(member.joinedTimestamp / 1000)}:T>`;

    const welcomeEmbed = new EmbedBuilder()
        .setColor('#2b2d31')
        .setTitle('New member!')
        .setDescription(
            `🎉 Hi\n<@!${member.id}>\n` +
            `Welcome to the best cfg in Poland!\n` +
            `Go check out our stuff!\n\n` +
            `**You're our ${member.guild.memberCount} member!**\n\n` +
            `**Member Info:**\n` +
            `🪪 **Discord account created:**\n${createdAt}\n` +
            `👤 **Username:** \`${member.user.username}\`\n` +
            `📅 **Joined at:** ${joinedAt}`
        )
        .setThumbnail(member.guild.iconURL({ dynamic: true }) || client.user.displayAvatarURL());

    channel.send({ embeds: [welcomeEmbed] });
});

// --- BOOSTY SERWERA ---
client.on('guildMemberUpdate', async (oldMember, newMember) => {
    if (!oldMember.premiumSince && newMember.premiumSince) {
        const channel = newMember.guild.systemChannel || newMember.guild.channels.cache.find(ch => ch.type === ChannelType.GuildText);
        if (!channel) return;

        const boostEmbed = new EmbedBuilder()
            .setColor('#ff73fa')
            .setTitle('💎 New server Boost!')
            .setDescription(
                `<@!${newMember.id}> **BOOST!**\n` +
                `> thanks for boosting our server!\n` +
                `> Go check out our booster zone!\n\n` +
                `**Boost Info:**\n` +
                `🧊 Server Boost level: \`${newMember.guild.premiumTier}\`\n` +
                `🔢 Boost count: \`${newMember.guild.premiumSubscriptionCount}\``
            )
            .setThumbnail(newMember.user.displayAvatarURL({ dynamic: true }))
            .setImage(BANNER_URL);

        channel.send({ embeds: [boostEmbed] });
    }
});

// --- OBSŁUGA INTERAKCJI (Komendy oraz Przyciski) ---
client.on('interactionCreate', async (interaction) => {
    
    // Obsługa Przycisków (Weryfikacja oraz Tickety)
    if (interaction.isButton()) {
        // Weryfikacja (Przycisk "Zweryfikuj")
        if (interaction.customId === 'verify_btn') {
            const roleId = ACCEPT_ROLES[0]; // Możesz dopasować główną rolę weryfikacji
            const member = interaction.member;
            if (member.roles.cache.has(roleId)) {
                return interaction.reply({ content: 'Jesteś już zweryfikowany!', ephemeral: true });
            }
            try {
                await member.roles.add(roleId);
                await interaction.reply({ content: 'Pomyślnie zweryfikowano!', ephemeral: true });
            } catch (e) {
                interaction.reply({ content: 'Błąd podczas nadawania roli.', ephemeral: true });
            }
        }

        // System Ticketów (Tworzenie kanału)
        if (interaction.customId.startsWith('ticket_')) {
            const ticketType = interaction.customId.replace('ticket_', '');
            const categoryId = TICKET_CATEGORIES[ticketType];
            const allowedRoles = TICKET_ROLES[ticketType] || [];

            await interaction.deferReply({ ephemeral: true });

            try {
                // Konfiguracja uprawnień kanału ticketu
                const permissionOverwrites = [
                    {
                        id: interaction.guild.id,
                        deny: [PermissionFlagsBits.ViewChannel]
                    },
                    {
                        id: interaction.user.id,
                        allow: [PermissionFlagsBits.ViewChannel, PermissionFlagsBits.SendMessages, PermissionFlagsBits.ReadMessageHistory]
                    },
                    {
                        id: client.user.id,
                        allow: [PermissionFlagsBits.ViewChannel, PermissionFlagsBits.SendMessages, PermissionFlagsBits.ManageChannels]
                    }
                ];

                // Dodanie uprawnień dla ról administracyjnych obsługujących dany ticket
                allowedRoles.forEach(roleId => {
                    permissionOverwrites.push({
                        id: roleId,
                        allow: [PermissionFlagsBits.ViewChannel, PermissionFlagsBits.SendMessages, PermissionFlagsBits.ReadMessageHistory]
                    });
                });

                const channelName = `ticket-${ticketType}-${interaction.user.username}`.toLowerCase();
                const ticketChannel = await interaction.guild.channels.create({
                    name: channelName,
                    type: ChannelType.GuildText,
                    parent: categoryId || null,
                    permissionOverwrites: permissionOverwrites
                });

                // Przygotowanie pingu ról
                const rolePings = allowedRoles.map(r => `<@&${r}>`).join(' ');

                const ticketEmbed = new EmbedBuilder()
                    .setColor('#2b2d31')
                    .setTitle(`Ticket: ${ticketType.toUpperCase()}`)
                    .setDescription(`Witaj <@!${interaction.user.id}>!\nAdministracja wkrótce odpowie na Twoje zgłoszenie.`);

                await ticketChannel.send({ 
                    content: `${rolePings} <@!${interaction.user.id}>`, 
                    embeds: [ticketEmbed] 
                });

                await interaction.editReply({ content: `Utworzono Twój ticket: <#${ticketChannel.id}>` });
            } catch (e) {
                console.error(e);
                await interaction.editReply({ content: 'Wystąpił błąd podczas tworzenia kanału ticketu.' });
            }
        }
        return;
    }

    if (!interaction.isChatInputCommand()) return;
    const { commandName } = interaction;

    // --- /say ---
    if (commandName === 'say') {
        const msg = interaction.options.getString('message');
        const embed = new EmbedBuilder().setColor('#2b2d31').setDescription(msg)
            .setFooter({ text: `${client.user.username} • Today, Ad made by ${interaction.user.username}` });
        await interaction.reply({ embeds: [embed] });
    }

    // --- /bandc ---
    if (commandName === 'bandc') {
        const target = interaction.options.getUser('target');
        const reason = interaction.options.getString('reason');
        await interaction.guild.members.ban(target, { reason });
        const embed = new EmbedBuilder().setColor('#ff0000').setTitle('🔨 User has been banned for life')
            .addFields(
                { name: '👤 User', value: `<@!${target.id}>`, inline: true },
                { name: '🆔 ID', value: `\`${target.id}\``, inline: true },
                { name: '🛡️ Administrator', value: `<@${interaction.user.id}>`, inline: false },
                { name: '📝 Reason', value: `\`\`\`\n${reason}\n\`\`\``, inline: false }
            ).setImage(BANNER_URL);
        await interaction.reply({ embeds: [embed] });
    }

    // --- /unbandc ---
    if (commandName === 'unbandc') {
        const userId = interaction.options.getString('userid');
        const reason = interaction.options.getString('reason') || 'Brak powody';
        await interaction.guild.members.unban(userId, reason);
        const embed = new EmbedBuilder().setColor('#00ff00').setTitle('🔓 User has been unbanned')
            .addFields(
                { name: '👤 User', value: `<@!${userId}>`, inline: true },
                { name: '🆔 ID', value: `\`${userId}\``, inline: true },
                { name: '🛡️ Administrator', value: `<@${interaction.user.id}>`, inline: false },
                { name: '📝 Reason', value: `\`\`\`\n${reason}\n\`\`\``, inline: false }
            ).setImage(BANNER_URL);
        await interaction.reply({ embeds: [embed] });
    }

    // --- /minigame ---
    if (commandName === 'minigame') {
        const embed = new EmbedBuilder()
            .setColor('#2b2d31')
            .setTitle("🐱 We're sorry!")
            .setDescription(
                `<@!${interaction.user.id}>, this time you didn't win anything. Try your luck again tomorrow!\n\n` +
                `**Some Info:**\n` +
                `*Your chance was* **1** *in* **35**.\n\n` +
                `*We wish you better luck next time!*`
            )
            .setThumbnail(interaction.user.displayAvatarURL({ dynamic: true }))
            .setImage(BANNER_URL); // Użyje głównego bannera (możesz podmienić na osobny link)

        await interaction.reply({ embeds: [embed] });
    }

    // --- /accept ---
    if (commandName === 'accept') {
        const targetMember = interaction.options.getMember('target');
        try {
            await targetMember.roles.add(ACCEPT_ROLES);
            await interaction.reply({ content: `Pomyślnie nadano role użytkownikowi <@!${targetMember.id}>!`, ephemeral: true });
        } catch (e) {
            await interaction.reply({ content: 'Nie udało się nadać ról. Sprawdź uprawnienia bota.', ephemeral: true });
        }
    }

    // --- /setup (Wysyła panel weryfikacji i ticketów na kanał) ---
    if (commandName === 'setup') {
        // Panel weryfikacji
        const verifyEmbed = new EmbedBuilder()
            .setColor('#2ecc71')
            .setTitle('Verification')
            .setDescription('Click on verification to get access to the channels');
        
        const verifyRow = new ActionRowBuilder().addComponents(
            new ButtonBuilder().setCustomId('verify_btn').setLabel('Zweryfikuj').setStyle(ButtonStyle.Success)
        );

        // Panel ticketów
        const ticketEmbed = new EmbedBuilder()
            .setColor('#3498db')
            .setTitle('🎫 Tickets')
            .setDescription(
                'Want to place an order, need to contact the owner or staff for help?\n' +
                'Click the appropriate button below to open a private channel with the administration.\n\n' +
                "Please don't open the tickets without a proper reason."
            );

        const ticketRow1 = new ActionRowBuilder().addComponents(
            new ButtonBuilder().setCustomId('ticket_shop').setLabel('Shop 🛒').setStyle(ButtonStyle.Success),
            new ButtonBuilder().setCustomId('ticket_owner').setLabel('Owner 👑').setStyle(ButtonStyle.Secondary),
            new ButtonBuilder().setCustomId('ticket_support').setLabel('Support ❓').setStyle(ButtonStyle.Primary)
        );

        const ticketRow2 = new ActionRowBuilder().addComponents(
            new ButtonBuilder().setCustomId('ticket_recruitment').setLabel('Recruitment 📄').setStyle(ButtonStyle.Danger),
            new ButtonBuilder().setCustomId('ticket_partner').setLabel('Partnership 🤝').setStyle(ButtonStyle.Secondary)
        );

        await interaction.channel.send({ embeds: [verifyEmbed], components: [verifyRow] });
        await interaction.channel.send({ embeds: [ticketEmbed], components: [ticketRow1, ticketRow2] });
        await interaction.reply({ content: 'Wysłano panele!', ephemeral: true });
    }
});

client.login(process.env.DISCORD_TOKEN);