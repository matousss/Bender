��    q      �  �   ,      �	     �	     �	     �	     �	     �	     �	     �	     �	     
     
     
     1
     9
  
   G
     R
     f
     �
     �
     �
     �
     �
     �
     �
                @     U     p  #   �     �     �     �               '     @     Y     l     �     �     �     �     �               <     S     l     �     �     �     �     �          $     7     Q     e     �     �     �     �     �     �             	   :     D     X     `  
   f     q     �     �     �     �     �     �     �     �            	   0     :     J     [     g     s     {  
   �     �     �     �     �     �     �  
   �     �            	   +     5     C     O     ]     c     q     �     �     �     �     �     �          $     <     Q  6   n  6   �  �   �     b     w     �  "   �     �  )   �     �               :  &   C     j  '   �  K   �  	   �       <     %   V     |     �  )   �  &   �  +     &   2  P   Y  ;   �     �     �  j        ~     �  (   �  �   �     �  (   �  5     n   I     �  C   �  �     =  �  C      P   `      �      �      �   `   �      _!     p!     �!  *   �!     �!  0   �!  l   �!     h"  �   p"  J   h#     �#     �#     �#     �#     �#  
   $  +   $  
   =$  +   H$  ,   t$  ,   �$     �$     �$  6   %  5   ;%     q%  1   ~%  &   �%  2   �%  ?   
&     J&  +   d&     �&     �&     �&      �&  )   �&     ''  )   :'  0   d'     �'     �'     �'  >   �'     �'  &   (     A(     T(     c(  (   p(     �(     �(  2   �(     �(  8   �(  #   7)  $   [)  A   �)     g              4              O   a   B   &          H          A       C           `       Y   (                         .       Z   P   m          ]   [   l   S      K   Q      T         F   	       e             p   $          n   7   0       -   1   G      2      d   ,   \       8      )      #   %   b   3          R   f   ;          +         5   h   U       X       M       V          '          L           "   k       N   <   6   9       >       :   o      /      E   D   q   c   j       J   i   W          ^   
   _   I   ?   !       *       @      =            %d queue_more %s %s kicked %s %s moved %s added_to_queue %s error_not_owner %s error_too_long %s info %s invalid_argument %s join %s no_page_error %s on_cooldown_error %s ping %s queue_full %s removed %s showing_help_for %s translate_error_invalid_code aliases already_connected_error already_paused_error bot_missing_permissions_error bot_not_connected_error channel channel_empty channel_not_match_error cog_googletranslator_description cog_info_description cog_moderation_description cog_settings_description cog_voiceclientcommands_description cog_youtubemusic_description command_disconnect_description command_help_description command_help_tips command_help_usage command_info_description command_join_description command_join_usage command_kick_all_description command_kick_all_usage command_kick_description command_kick_others_description command_kick_others_usage command_kick_usage command_loop_description command_move_all_description command_move_all_usage command_move_description command_move_others_description command_move_others_usage command_move_usage command_nowplaying_description command_pause_description command_ping_description command_play_description command_play_usage command_queue_description command_queue_usage command_remove_description command_remove_usage command_resume_description command_skip_description command_skip_usage command_translate_description command_translate_usage command_usage commands_with_no_category emptiness empty_channel_error ends_in found guild_only help_categories help_categories_description join_error_same_channel leave_error loop_off loop_on message_too_long missing_parameters_error no_category no_category_or_command no_channel_error no_result not_found_error not_paused_error not_playing now_playing on_join paused play_error playing_error_different_channel position position_error possible_command_tips possible_commands queue queue_full queue_size_error resumed same_channels_error searching song_duration subcommands timeout_error title track_stacked translate_error_invalid_code unexpected_error unknow_join_error unknow_playing_error unknown_remove_error user_not_connected_error Project-Id-Version: 
Report-Msgid-Bugs-To: 
PO-Revision-Date: 2021-05-02 21:16+0200
Last-Translator: 
Language-Team: 
Language: en
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: plurals=2; plural=(n > 1);
X-Generator: Poedit 2.4.2
 And %d more... I've kicked %s from %s. I've moved %s to %s. %s songs were added to queue You are not owner %s! This command is only for owner!  %s is too long, I can play only songs shorter than 2h! I'm multipurpose discord bot created with library discord.py.
[https://github.com/Rapptz/discord.py]
Currently running version is %s. Invalid argument: %s Connected to %s There's no page %s. This command is on cooldown for %s Ping: %s Queue is full! Some song wasn't added %s. Removed %s from queue. Showing help for %s: %s is invalid language code! Aliases: I'm already connected to that channel! ⏯️ Music is already paused I'm missing permission for that action! Cannot perform that action. because I'm not connected to any voice channel! Uploader: Channel is empty. You have to be in same channel as me to perform that action! Commands to help you with translation Information related commands Moderation related commands Commands to customize behavior of the bot Commands related to bot's voice client You can play some music with these commands Disconnect bot from any voice channel. Show help for command or category.
``help commands`` show all possible commands. [] - Optional argument <> - Required argument {} - Expected [command/category] Show basic info about bot Connect bot to specified voice channel.
If no channel is specified it will try to join your voice channel. [channel name] Disconnect all members from specified voice channel.
If channel is not specified takes channel of user, who invoked command.
You can specify members and roles by mentioning. Not specified users will stay in voice channel.
When there's no mentions, bot will disconnect everyone in channel. [channel] [@member] [@member] [@role]... Disconnect members from specified voice channel.
If channel is not specified takes channel of user, who invoked command.
You can specify members and roles by mentioning them.
When there's no mentions, bot will disconnect everyone in channel. Disconnect all members from specified voice channel.
If channel is not specified takes channel of user, who invoked command.
You can specify members and roles by mentioning. Not specified users will stay in voice channel.
When there's no mentions, bot will disconnect everyone in channel. [channel] [@member] [@member] [@role]... [all/others] [channel] [@member] [@member] [@role]... Turn on loop mode. 
When is loop mode active every played song will be added on end of the queue, when it end. Disconnect all members from specified voice channel.
If channel is not specified takes channel of user, who invoked command.
You can specify members and roles by mentioning. Not specified users will stay in voice channel.
When there's no mentions, bot will disconnect everyone in channel. [from channel] <destination channel> [@member] [@member] [@role]... Move users to specific channel.
If source channel wasn't specified source channel is channel, to which is connected user who invoked command.
You can specify users or roles by mentioning them. Disconnect all members from specified voice channel.
If channel is not specified takes channel of user, who invoked command.
You can specify members and roles by mentioning them to exclude them from disconnection.
When there's no mentions, bot will disconnect everyone in channel except user, who invoked the command. [from channel] <destination channel> [@member] [@member] [@role]... [all/others] [from channel] <destination channel> [@member] [@member] [@role]... Show info about current song Pause currently playing music Show bot latency. Connect bot to voice channel of user, who invoked the command, then search for song and play it. <url/song title> Show current queue. [page] Remove song on specific position in queue. <position in queue> When is music paused this command can resume it. Skip certain amount of songs.
⚠️ Warning: If loop mode is on, songs will be removed from queue for good! [count] Translate given text using google translator.
You can specify source language and destination language.
When destination language wasn't specified text will be translated to default language of guild.
Example: ``,translate {en} {de} Hello World!`` [[{source language code}] {destination language code}] <text to translate> Usage: Uncategorized commands Wow, such empty Specified channel is empty. Ends in: 🎵 Found This command can be executed only in guild. Categories Show help for category with help <category> Source and destination are the same channel. Error occurred when trying to leave channel. ▶️ Loop mode deactivated 🔁 Loop mode activated Your message is too long, please split it to multiple. Missing arguments! Check you syntax and try it again. No category: Command or category with that name doesn't exist. I'm not connected to any voice channel I didn't find anything try checking your spelling. I haven't found anything. Check your spelling and try it again. ⏯️ Bot is not paused. 🔇 Bot is currently not playing anything. Currently playing Use ``,help`` to show help. ⏸️ Music has been paused. Error while trying to play song. I'm already playing in different channel. Position in queue: On that position in queue isn't any song. Show help for each command with "help <command>" Possible commands: Queue: Queue is full! Given number is greater than queue size -> Skipping all ⏭️ ▶️ Continue playing now. Destination and source channels match. 🔎 Searching…  Song duration: Subcommands: Connection timeout, please try it again. Title: Track got stuck Specified language code or both codes are invalid. Unexpected error occurred. Unknown error occurred when connecting to voice channel. Error occurred while playing music. Error occurred while removing songs. You have to be connected to voice channel to perform that action. 