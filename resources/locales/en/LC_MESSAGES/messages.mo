��    v      �  �   |      �	     �	     �	     
     
     *
     >
     P
     c
     u
     }
     �
     �
     �
     �
     �
     �
  
   �
     �
     
          *     ?     ]     u     }     �     �     �     �  #   �          -     L     e     w     �     �     �     �     �               6     I     b          �     �     �     �     �          5     N     g     z     �     �     �     �     �  $        4  "   S     v     �     �     �     �     �  	   �               #  
   )     4     D     `     x     �     �     �     �     �     �     �     �                    #  
   *     5     U     ^     m     �     �     �     �  
   �     �     �     �  	   �                    -     3     A     R     e     {     �     �     �  6  �          +     C     X     u     �  6   �  6   �  �        �     �     �  "   �     �     �  )        >     U     j  &   s     �  '   �  K   �  	   -     7  <   I     �     �  )   �  &   �  +     %   <  N   b  -   �     �     �  h        u  �  �  (     Y  6  (   �  5   �  l   �  �  \  C   �  (  (  �  Q   C   �!  P   :"     �"     �"     �"  _   �"     7#     H#     [#  )   b#     �#  /   �#  -   �#  A   �#     @$  *   T$     $     �$  k   �$     %     %     %     3%     C%     _%  
   h%  +   s%  
   �%  /   �%  ,   �%  ,   &     4&     Q&  5   j&     �&  1   �&     �&  ?   �&     >'  $   Z'     '     �'     �'      �'  )   �'     (  )   )(  0   S(     �(     �(  .   �(     �(     �(  >   �(     .)  &   K)     r)     �)     �)  (   �)     �)     �)     �)  8   �)  #   5*  $   Y*  7   ~*  7   �*  E   �*     ^   2       .   k   8      K   @           5   `   U       &   ?   :           e          
           L   E   ]           P   d         X   "   j              *   f   /   u           o   >   F   C       )   s       Q      Z       ,      9   h       \   i   1       l         -   a      T              I   [           D      M   G                  Y   H         3      	      _             B   O       q   6   N   p   b         4   +       ;   t   A   =      !       $       0   g   '   V       (           n      c       W       R      m          <   %       S   r   J         #   7       v       %d queue_more %s %s kicked %s %s moved %s added_to_queue %s current_language %s current_prefix %s error_not_owner %s error_too_long %s info %s invalid_argument %s join %s no_page_error %s on_cooldown_error %s ping %s possible_languages %s queue_full %s removed %s showing_help_for aliases already_connected_error already_paused_error bot_missing_permissions_error bot_not_connected_error channel channel_empty channel_not_match_error cog_info_description cog_moderation_description cog_settings_description cog_voiceclientcommands_description cog_youtubemusic_description command_disconnect_description command_help_description command_help_tips command_help_usage command_info_description command_join_description command_join_usage command_kick_all_description command_kick_all_usage command_kick_description command_kick_others_usage command_kick_usage command_loop_description command_move_all_description command_move_all_usage command_move_description command_move_others_description command_move_others_usage command_move_usage command_nowplaying_description command_pause_description command_ping_description command_play_description command_play_usage command_queue_description command_queue_usage command_remove_description command_remove_usage command_resume_description command_setting_description command_setting_language_description command_setting_language_usage command_setting_prefix_description command_setting_prefix_usage command_setting_usage command_skip_description command_skip_usage command_usage commands_with_no_category emptiness empty_channel_error ends_in found guild_only help_categories help_categories_description join_error_same_channel leave_error loop_off loop_on missing_parameters_error no_category no_category_or_command no_channel_error not_found_error not_paused_error not_playing now_playing on_join paused play_error playing_error_different_channel position position_error possible_command_tips possible_commands possible_settings prefix_too_long_error queue queue_full queue_size_error resumed same_channels_error searching song_duration subcommands timeout_error title track_stacked unexpected_error unknown_join_error unknown_playing_error unknown_remove_error unknown_setting_language_error unknown_setting_prefix_error user_not_connected_error Project-Id-Version: Bender
Report-Msgid-Bugs-To: 
PO-Revision-Date: 2021-05-04 01:04+0200
Last-Translator: matousss
Language-Team: matousss
Language: en
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: plurals=2; plural=(n > 1);
X-Generator: Poedit 2.4.2
 And %d more... I've kicked %s from %s. I've moved %s to %s. %s songs were added to queue Current language is %s. Current prefix is %s. You are not owner %s! This command is only for owner!  %s is too long, I can play only songs shorter than 2h! I'm multipurpose discord bot created with library discord.py.
[https://github.com/Rapptz/discord.py]
Currently running version is %s. Invalid argument: %s Connected to %s There's no page %s. This command is on cooldown for %s Ping: %s Supported languages: %s Queue is full! Some song wasn't added %s. Removed %s from queue. Showing help for %s: Aliases: I'm already connected to that channel! ⏯️ Music is already paused I'm missing permission for that action! Cannot perform that action. because I'm not connected to any voice channel! Uploader: Channel is empty. You have to be in same channel as me to perform that action! Information related commands Moderation related commands Commands to customize behavior of the bot Commands related to bot's voice client You can play some music with these commands Disconnect bot from any voice channel Show help for command or category
``help commands`` show all possible commands [] - Optional argument <> - Required argument [command/category] Show basic info about bot Connect bot to specified voice channel
If no channel is specified it will try to join your voice channel [channel name] Disconnect all members from specified voice channel
If channel is not specified takes channel of user, who invoked command
You can specify members and roles by mentioning. Not specified users will stay in voice channel
When there's no mentions, bot will disconnect everyone in channel
To split source and destination channel use ``;``. If name of channel contain ``;`` replace it with ``.|``. [channel] [@member] [@member] [@role]... Disconnect members from specified voice channel
If channel is not specified takes channel of user, who invoked command.
You can specify members and roles by mentioning them
When there's no mentions, bot will disconnect everyone in channel
To split source and destination channel use ``;``. If name of channel contain ``;`` replace it with ``.|`` [channel] [@member] [@member] [@role]... [all/others] [channel] [@member] [@member] [@role]... Turn on loop mode 
When is loop mode active every played song will be added on end of the queue, when it end Disconnect all members from specified voice channel
If channel is not specified takes channel of user, who invoked command
You can specify members and roles by mentioning. Not specified users will stay in voice channel
When there's no mentions, bot will disconnect everyone in channel
To split source and destination channel use ``;``. If name of channel contain ``;`` replace it with ``.|`` [from channel] <destination channel> [@member] [@member] [@role]... Move users to specific channel
If source channel wasn't specified source channel is channel, to which is connected user who invoked command
You can specify users or roles by mentioning them
To split source and destination channel use ``;``. If name of channel contain ``;`` replace it with ``.|`` Disconnect all members from specified voice channel
If channel is not specified takes channel of user, who invoked command
You can specify members and roles by mentioning them to exclude them from disconnection
When there's no mentions, bot will disconnect everyone in channel except user, who invoked the command
To split source and destination channel use ``;``. If name of channel contain ``;`` replace it with ``.|`` [from channel] <destination channel> [@member] [@member] [@role]... [all/others] [from channel] <destination channel> [@member] [@member] [@role]... Show info about current song Pause currently playing music Show bot latency Connect bot to voice channel of user, who invoked the command, then search for song and play it <url/song title> Show current queue [page] Remove song on specific position in queue <position in queue> When is music paused this command can resume it This command is for customizing bots behavior Change language of messages, which bot sendsWorks only for guild [new language code] Change command prefix to whatever you want [new prefix] <option> [new value] Skip certain amount of songs
⚠️ Warning: If loop mode is on, songs will be removed from queue for good! [count] Usage: Uncategorized commands Wow, such empty Specified channel is empty. Ends in: 🎵 Found This command can be executed only in guild. Categories Show help for category with ``help <category>`` Source and destination are the same channel. Error occurred when trying to leave channel. ▶️ Loop mode deactivated 🔁 Loop mode activated Missing arguments! Check you syntax and try it again. No category: Command or category with that name doesn't exist. Cannot find specified channel. I haven't found anything. Check your spelling and try it again. ⏯️ Music is not paused. 🔇 Music is not playing currently. Currently playing Use ``,help`` to show help. ⏸️ Music has been paused. Error while trying to play song. I'm already playing in different channel. Position in queue: On that position in queue isn't any song. Show help for each command with "help <command>" Possible commands: Possible settings: Prefix is too long, please choose shorter one. Queue: Queue is full! Given number is greater than queue size -> Skipping all ⏭️ ▶️ Continue playing now. Destination and source channels match. 🔎 Searching…  Song duration: Subcommands: Connection timeout, please try it again. Title: Track got stuck Unexpected error occurred. Unknown error occurred when connecting to voice channel. Error occurred while playing music. Error occurred while removing songs. Error occurred while trying to change language setting. Error occurred while trying to change language setting. You have to be connected to the voice channel to perform that action. 