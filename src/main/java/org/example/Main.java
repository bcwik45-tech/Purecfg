package org.example;

import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.JDA;
import net.dv8tion.jda.api.JDABuilder;
import net.dv8tion.jda.api.Permission;
import net.dv8tion.jda.api.entities.User;
import net.dv8tion.jda.api.entities.channel.concrete.TextChannel;
import net.dv8tion.jda.api.events.guild.member.GuildMemberJoinEvent;
import net.dv8tion.jda.api.events.guild.member.update.GuildMemberUpdateBoostTimeEvent;
import net.dv8tion.jda.api.events.interaction.component.StringSelectInteractionEvent;
import net.dv8tion.jda.api.events.message.MessageReceivedEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;
import net.dv8tion.jda.api.interactions.components.selections.StringSelectMenu;
import net.dv8tion.jda.api.requests.GatewayIntent;
import org.jetbrains.annotations.NotNull;

import java.awt.Color;
import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Locale;

public class Main extends ListenerAdapter {

    private static final String WELCOME_CHANNEL_ID = "1561740336726937660";
    private static final String BOOST_CHANNEL_ID = "1568724452693516398";
    private static final String TICKET_COMMAND_CHANNEL_ID = "1561758533446410251";
    private static final String TICKET_TARGET_CHANNEL_ID = "1569025423248068669";

    // Rola nadawana automatycznie nowym użytkownikom
    private static final String AUTO_ROLE_ID = "1540360249775493230";

    // ID kategorii dla poszczególnych rodzajów ticketów
    private static final String CATEGORY_OWNER = "1567496735360811049";
    private static final String CATEGORY_SHOP = "1567497043134386226";
    private static final String CATEGORY_SUPPORT = "1567497448379645984";
    private static final String CATEGORY_PARTNER = "1568731769782534374";

    private static final String BANNER_URL = "https://cdn.discordapp.com/attachments/1563292364414648471/1569045074615079053/goatbanner.jpg?ex=6af20699&is=6af0b519&hm=3e51cadbe71abb286ecbcae3f6ac82e1002af6b3ea395174102164fdadc03b63&";

    public static void main(String[] args) throws Exception {
        String token = System.getenv("DISCORD_TOKEN");
        if (token == null || token.isEmpty()) {
            System.out.println("Błąd: Nie znaleziono zmiennej środowiskowej DISCORD_TOKEN!");
            return;
        }

        JDA jda = JDABuilder.createDefault(token)
                .enableIntents(
                        GatewayIntent.MESSAGE_CONTENT,
                        GatewayIntent.GUILD_MEMBERS,
                        GatewayIntent.GUILD_MESSAGES,
                        GatewayIntent.GUILD_MODERATION
                )
                .addEventListeners(new Main())
                .build();

        jda.awaitReady();
        System.out.println("Goatcfg Bot (Full Suite) wystartował pomyślnie!");
    }

    // 1. POWITANIA ORAZ AUTOMATYCZNE NADAWANIE ROLI
    @Override
    public void onGuildMemberJoin(@NotNull GuildMemberJoinEvent event) {
        var role = event.getGuild().getRoleById(AUTO_ROLE_ID);
        if (role != null) {
            event.getGuild().addRoleToMember(event.getMember(), role).queue();
        }

        TextChannel ch = event.getGuild().getTextChannelById(WELCOME_CHANNEL_ID);
        if (ch != null) {
            sendWelcomeMessage(ch, event);
        }
    }

    private void sendWelcomeMessage(TextChannel channel, GuildMemberJoinEvent event) {
        String createdAt = event.getUser().getTimeCreated().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        int memberCount = event.getGuild().getMemberCount();

        EmbedBuilder embed = new EmbedBuilder();
        embed.setColor(new Color(40, 40, 40));
        embed.setDescription(
                "🏆 **× Goatcfg × WITAJ NA SERWERZE**\n\n" +
                        "<:4_:1567955855318585364> " + event.getMember().getAsMention() + " **właśnie dołączył(a) na serwer Goatcfg!**\n" +
                        "> Liczymy, że zostaniesz z nami na dłużej!\n\n" +
                        "⭐ **Jesteś `" + memberCount + "` użytkownikiem na naszym serwerze!**\n" +
                        "👤 **Konto utworzone:** `" + createdAt + "`\n" +
                        "👑 **Numer członka:** `# " + memberCount + "`\n\n" +
                        "> Zweryfikuj się, zapoznaj się z regulaminem i baw się dobrze!"
        );
        embed.setImage(BANNER_URL);
        embed.setFooter("Goatcfg");

        String stickersText =
                "<:s_:1567489688032256041> " +
                        "<:1564005649770217603:1568728589036163264> " +
                        "<:6_:1568727905465401464> " +
                        "<:b_:1567490339907043388>";

        channel.sendMessage(stickersText).addEmbeds(embed.build()).queue();
    }

    // 2. BOOSTY SERWERA
    @Override
    public void onGuildMemberUpdateBoostTime(@NotNull GuildMemberUpdateBoostTimeEvent event) {
        if (event.getNewTimeBoosted() != null) {
            TextChannel ch = event.getGuild().getTextChannelById(BOOST_CHANNEL_ID);
            if (ch != null) {
                EmbedBuilder embed = new EmbedBuilder();
                embed.setColor(new Color(255, 110, 200));
                embed.setDescription(
                        "💎 **New server Boost!**\n\n" +
                                event.getMember().getAsMention() + " **BOOST!**\n" +
                                "> thanks for boosting our server!\n" +
                                "> *Go check out our booster zone!*\n\n" +
                                "🚀 **Boost level**\n" +
                                "> 🧊 **Server Boost level:** `" + event.getGuild().getBoostTier().getKey() + "`\n" +
                                "> 🔢 **Boost count:** `" + event.getGuild().getBoostCount() + "`"
                );
                embed.setImage(BANNER_URL);
                embed.setFooter("Goatcfg");

                String boostStickers =
                        "<:a_:1567489885365997638> " +
                                "<:s_:1567489688032256041> " +
                                "<:c_:1567490142908719155> " +
                                "<:b_:1567490339907043388>";

                ch.sendMessage(boostStickers).addEmbeds(embed.build()).queue();
            }
        }
    }

    // 3. OBSŁUGA KOMEND ORAZ PANEL TICKETÓW
    @Override
    public void onMessageReceived(@NotNull MessageReceivedEvent event) {
        if (event.getAuthor().isBot()) return;
        String msg = event.getMessage().getContentRaw();
        String[] args = msg.split("\\s+");

        if (msg.equalsIgnoreCase("!ping")) {
            event.getChannel().sendMessage("Pong! (Java JDA)").queue();
        }

        if (args[0].equalsIgnoreCase("!bandc")) {
            if (!event.getMember().hasPermission(Permission.BAN_MEMBERS)) {
                event.getChannel().sendMessage("Brak uprawnień do banowania!").queue();
                return;
            }
            if (args.length < 3) {
                event.getChannel().sendMessage("Użycie: `!bandc <dcid> <powód>`").queue();
                return;
            }

            String targetId = args[1].replaceAll("[^0-9]", "");
            StringBuilder reasonBuilder = new StringBuilder();
            for (int i = 2; i < args.length; i++) {
                reasonBuilder.append(args[i]).append(" ");
            }
            String reason = reasonBuilder.toString().trim();

            event.getJDA().retrieveUserById(targetId).queue(targetUser -> {
                event.getGuild().ban(targetUser, 0, java.util.concurrent.TimeUnit.DAYS).reason(reason).queue(success -> {
                    sendBanEmbed(event.getChannel().asTextChannel(), targetUser, event.getAuthor(), reason, "User banned permanently", new Color(220, 50, 50));
                }, error -> {
                    event.getChannel().sendMessage("Nie udało się zbanować użytkownika (sprawdź ID).").queue();
                });
            }, error -> {
                event.getChannel().sendMessage("Nie znaleziono użytkownika o takim ID.").queue();
            });
            return;
        }

        if (args[0].equalsIgnoreCase("!unbandc")) {
            if (!event.getMember().hasPermission(Permission.BAN_MEMBERS)) {
                event.getChannel().sendMessage("Brak uprawnień!").queue();
                return;
            }
            if (args.length < 3) {
                event.getChannel().sendMessage("Użycie: `!unbandc <dcid> <powód>`").queue();
                return;
            }

            String targetId = args[1].replaceAll("[^0-9]", "");
            StringBuilder reasonBuilder = new StringBuilder();
            for (int i = 2; i < args.length; i++) {
                reasonBuilder.append(args[i]).append(" ");
            }
            String reason = reasonBuilder.toString().trim();

            event.getJDA().retrieveUserById(targetId).queue(targetUser -> {
                event.getGuild().unban(targetUser).reason(reason).queue(success -> {
                    sendBanEmbed(event.getChannel().asTextChannel(), targetUser, event.getAuthor(), reason, "User unbanned", new Color(50, 220, 50));
                }, error -> {
                    event.getChannel().sendMessage("Nie udało się odbanować użytkownika.").queue();
                });
            }, error -> {
                event.getChannel().sendMessage("Nie znaleziono użytkownika o takim ID.").queue();
            });
            return;
        }

        if (msg.equalsIgnoreCase("!ticketsetup")) {
            if (!event.getChannel().getId().equals(TICKET_COMMAND_CHANNEL_ID)) {
                event.getChannel().sendMessage("Tej komendy można użyć tylko na wyznaczonym kanale!").queue();
                return;
            }

            event.getMessage().delete().queue();

            TextChannel targetChannel = event.getGuild().getTextChannelById(TICKET_TARGET_CHANNEL_ID);
            if (targetChannel == null) {
                event.getChannel().sendMessage("Nie znaleziono kanału docelowego dla panelu ticketów!").queue();
                return;
            }

            EmbedBuilder embed = new EmbedBuilder();
            embed.setColor(new Color(40, 40, 40));
            embed.setDescription(
                    "# Tickets\n\n" +
                            "```yaml\nTicket Owner\nOpen if you have a demand to the owners\n```\n" +
                            "```yaml\nTicket Shop\nopen if you you want to buy something\n```\n" +
                            "```yaml\nTicket Support\nOpen if you need any help\n```\n" +
                            "```yaml\nTicket Partner\nOpen if you want to collaborate with us.\n```\n\n" +
                            "For any issues, text on <#1568723402133348502>"
            );
            embed.setImage(BANNER_URL);
            embed.setFooter("Goatcfg");

            StringSelectMenu menu = StringSelectMenu.create("ticket_select")
                    .setPlaceholder("Select category...")
                    .addOption("Owner", "ticket_owner", "ticket with a matter for the config owners", net.dv8tion.jda.api.entities.emoji.Emoji.fromFormatted("👑"))
                    .addOption("Shop", "ticket_shop", "Ticket for purchase an item from our store", net.dv8tion.jda.api.entities.emoji.Emoji.fromFormatted("🛒"))
                    .addOption("Support", "ticket_support", "Support ticket for help in our config server", net.dv8tion.jda.api.entities.emoji.Emoji.fromFormatted("❓"))
                    .addOption("Partner", "ticket_partner", "Ticket for partnership", net.dv8tion.jda.api.entities.emoji.Emoji.fromFormatted("🤝"))
                    .build();

            targetChannel.sendMessageEmbeds(embed.build()).setActionRow(menu).queue();
        }

        if (msg.startsWith("!clear")) {
            if (!event.getMember().hasPermission(Permission.MESSAGE_MANAGE)) {
                event.getChannel().sendMessage("Brak uprawnień!").queue();
                return;
            }
            try {
                int amount = Integer.parseInt(msg.split(" ")[1]);
                event.getChannel().getHistory().retrievePast(amount).queue(messages -> {
                    ((TextChannel) event.getChannel()).purgeMessages(messages);
                });
            } catch (Exception e) {
                event.getChannel().sendMessage("Użycie: `!clear <ilość>`").queue();
            }
        }
    }

    private void sendBanEmbed(TextChannel channel, User target, User admin, String reason, String title, Color color) {
        EmbedBuilder embed = new EmbedBuilder();
        embed.setColor(color);
        embed.setDescription(
                "🔨 **" + title + "**\n\n" +
                        "👤 **User**\n" + target.getAsMention() + "\n\n" +
                        "🆔 **ID**\n`" + target.getId() + "`\n\n" +
                        "🛡️ **Administrator**\n" + admin.getAsMention() + "\n\n" +
                        "📝 **Reason**\n```yaml\n" + reason + "\n```"
        );
        embed.setImage(BANNER_URL);
        embed.setFooter("Goatcfg Security");

        channel.sendMessage(target.getAsMention()).addEmbeds(embed.build()).queue();
    }

    // 4. TWORZENIE KANAŁU TICKETA
    @Override
    public void onStringSelectInteraction(@NotNull StringSelectInteractionEvent event) {
        if (!event.getComponentId().equals("ticket_select")) return;

        String selected = event.getValues().get(0);
        String channelName = selected.replace("ticket_", "") + "-" + event.getUser().getName().toLowerCase();
        var guild = event.getGuild();
        var member = event.getMember();

        var channelAction = guild.createTextChannel(channelName);

        String targetCategoryId = "";
        if (selected.equals("ticket_owner")) targetCategoryId = CATEGORY_OWNER;
        else if (selected.equals("ticket_shop")) targetCategoryId = CATEGORY_SHOP;
        else if (selected.equals("ticket_support")) targetCategoryId = CATEGORY_SUPPORT;
        else if (selected.equals("ticket_partner")) targetCategoryId = CATEGORY_PARTNER;

        if (!targetCategoryId.isEmpty() && guild.getCategoryById(targetCategoryId) != null) {
            channelAction.setParent(guild.getCategoryById(targetCategoryId));
        }

        channelAction
                .addPermissionOverride(guild.getPublicRole(), 0L, Permission.VIEW_CHANNEL.getRawValue())
                .addPermissionOverride(member, Permission.VIEW_CHANNEL.getRawValue(), 0L)
                .queue(channel -> {
                    if (selected.equals("ticket_owner")) {
                        addRoleToChannel(channel, "1567496735360811049");
                        addRoleToChannel(channel, "1540359821323149392");
                        addRoleToChannel(channel, "1540495893399081061");
                    } else if (selected.equals("ticket_shop")) {
                        addRoleToChannel(channel, "1567497043134386226");
                        addRoleToChannel(channel, "1540359821323149392");
                        addRoleToChannel(channel, "1540495893399081061");
                    } else if (selected.equals("ticket_support")) {
                        addRoleToChannel(channel, "1567497448379645984");
                        addRoleToChannel(channel, "1568725620601524254");
                    } else if (selected.equals("ticket_partner")) {
                        addRoleToChannel(channel, "1568725620601524254");
                    }

                    event.reply("Twój ticket został utworzony: " + channel.getAsMention()).setEphemeral(true).queue();

                    String categoryTitle = selected.replace("ticket_", "").toUpperCase(Locale.ROOT);
                    String formattedDate = OffsetDateTime.now().format(DateTimeFormatter.ofPattern("dd MMMM yyyy, HH:mm", new Locale("en", "US")));

                    EmbedBuilder ticketEmbed = new EmbedBuilder();
                    ticketEmbed.setColor(new Color(40, 40, 40));
                    ticketEmbed.setDescription(
                            "• **" + categoryTitle + " 🛒**\n\n" +
                                    "**Open date:** " + formattedDate + "\n" +
                                    "**Opening user:** " + member.getAsMention() + "\n\n" +
                                    "**Description:** Please give us details about your reason to open this ticket.\n\n" +
                                    "Click the button below to close the ticket."
                    );
                    ticketEmbed.setFooter("Goatcfg");

                    channel.sendMessage(member.getAsMention()).addEmbeds(ticketEmbed.build())
                            .setActionRow(net.dv8tion.jda.api.interactions.components.buttons.Button.danger("close_ticket", "Close Ticket 🔒"))
                            .queue();
                });
    }

    private void addRoleToChannel(TextChannel channel, String roleId) {
        var role = channel.getGuild().getRoleById(roleId);
        if (role != null) {
            channel.getManager().putPermissionOverride(role, Permission.VIEW_CHANNEL.getRawValue(), 0L).queue();
        }
    }

    @Override
    public void onButtonInteraction(@NotNull net.dv8tion.jda.api.events.interaction.component.ButtonInteractionEvent event) {
        if (event.getComponentId().equals("close_ticket")) {
            event.reply("Zamykanie ticketu...").setEphemeral(true).queue();
            if (event.getChannel() instanceof TextChannel) {
                event.getChannel().asTextChannel().delete().queue();
            }
        }
    }
}