import _queue
import datetime
import typing
from queue import Queue
import youtube_dl
from discord import FFmpegPCMAudio
from discord import VoiceClient
from discord import utils
from discord.ext import commands
from discord.ext import tasks
from .messages import MessagesTexts as Messages
from .utils import benderUtils

YTDL_OPTIONS = {
    'format': 'bestaudio',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                  'options': '-vn'}


class YoutubeMusic(commands.Cog):
    @tasks.loop(seconds=180, count=None)
    async def event_loop(self):
        print("<INFO> Starting garbage collection...")

        for player_key in self.music_players:
            player = self.music_players[player_key]

            if player.destroy is True:
                print("<INFO><GARBAGE_COLLECTOR> Found inactive one... \n Key = " + player.key)
                await player.voice_client.disconnect()
                print("<INFO><GARBAGE_COLLECTOR> Destroying...")
                self.music_players.removekey(player.key)
                print("<INFO><GARBAGE_COLLECTOR> Destroyed!")

        print("<INFO> Garbage collected!")

    def __init__(self, bot):

        self.bot = bot
        print("Initialized modules.audio.YoutubeMusic")
        self.music_players = Players()
        self.event_loop.start()

    @commands.command(name="join", aliases=["j", "summon"], description=Messages.join_des, brief=Messages.join_brief)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def _join(self, ctx, channel: typing.Optional[str] = None):
        if channel is not None:
            destination = benderUtils.getChannel(channel)
            # if channel.startswith("<#"):
            #     destination = utils.get(ctx.guild.channels, id=int(channel[2:].replace(">", "")))
            # elif channel.isnumeric():
            #     destination = utils.get(ctx.guild.channels, id=int(channel))
            # else:
            #     destination = utils.get(ctx.guild.channels, name=channel)
        elif ctx.author.voice and ctx.author.voice.channel:
            destination = ctx.author.voice.channel
        else:
            await ctx.send(Messages.join_error)
            return

        if ctx.voice_client and ctx.voice_client.is_connected() and channel is None:
            if ctx.author.voice.channel.guild == ctx.guild and ctx.voice_client.channel == ctx.author.voice.channel:
                await ctx.send(Messages.join_error_b)
            else:
                try:
                    await ctx.voice_client.move_to(destination)
                    await ctx.send(Messages.join + destination.name)

                except:
                    await ctx.send(Messages.join_error)
                return

        try:
            await destination.connect()
            await ctx.send(Messages.join + destination.name)
            print("<INFO> Joined channel " + destination.name + "#" + str(destination.id))
            self.music_players.add(str(ctx.guild.id), MusicPlayer(str(ctx.guild.id), ctx.voice_client))

        except:
            if destination is None:
                print("<ERROR> Error occurred while joining channel: no channel specified or user is not in channel")
            else:
                print("<ERROR> Error occurred while joining " + destination.name + "#" + str(destination.id))
            await ctx.send(Messages.join_error)
        pass

    @commands.command(name="leave", aliases=["dis", "disconnect", "l"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def _leave(self, ctx):
        channel = utils.get(self.bot.voice_clients, guild=ctx.guild)
        if channel is None:
            await ctx.send(Messages.leave_error)
            return
        if str(ctx.guild.id) in self.music_players:
            self.music_players.removekey(str(ctx.guild.id))
        await channel.disconnect()
        await ctx.send(Messages.leave)

        pass

    pass

    @commands.command(name="play", aliases=["p"])
    async def _play(self, ctx, *, what: str):
        if not ctx.voice_client:
            if ctx.author.voice and ctx.author.voice.channel:

                destination = ctx.author.voice.channel

                try:
                    await destination.connect()
                    await ctx.send(Messages.join + destination.name)
                    print("<INFO> Joined channel " + destination.name + "#" + str(destination.id))
                except:
                    print("<ERROR> Error occurred while joining " + destination.name + "#" + str(destination.id))
                    await ctx.send(Messages.join_error)
            else:
                await ctx.send(Messages.join_error)
                return
        # with youtube_dl.YoutubeDL(YTDL_OPTIONS) as ytdl:
        #
        #     if ctx.voice_client and not ctx.voice_client.is_playing():
        #         if play.startswith("https://www.youtube.com/watch?v="):
        #             # video = pafy.new(play)
        #             # bestsource = video.getbestaudio()
        #             # playable = bestsource.url
        #
        #             song_info = ytdl.extract_info(play, download=False)
        #
        #         else:
        #
        #             results = ytdl.extract_info(f"ytsearch:{play}", download=False)
        #             song_info = results["entries"][0]
        #
        #         ctx.voice_client.play(FFmpegPCMAudio(song_info["formats"][0]["url"], **FFMPEG_OPTIONS))
        #
        #     else:
        #
        #         await MessagesHandler.sendMessage(self, ctx, "error.notSupported")
        #         return
        #
        if not Players[int(ctx.guild.id)]:
            self.music_players.add(str(ctx.guild.id), MusicPlayer(str(ctx.guild.id), ctx.voice_client))
        else:
            self.music_players.add(str(ctx.guild.id), MusicPlayer(str(ctx.guild.id), ctx.voice_client))
            self.music_players[str(ctx.guild.id)].destroy = False
            await self.music_players[str(ctx.guild.id)].play(ctx, what)

        pass

    @commands.command(name="skip")
    async def _skip(self, ctx):
        await self.music_players[str(ctx.guild.id)].skip()
        await ctx.send("Skipping..")

    pass

    @commands.command(name="nowplaying", aliases=["np"])
    async def _nowplaying(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_connected:
            if ctx.voice_client.is_playing():
                if self.music_players[str(ctx.guild.id)]:
                    await ctx.send("Now is playing: `" + str(self.music_players[str(ctx.guild.id)].now_playing["title"]) + "`")
                else:
                    await ctx.send("Soundboard is now using voice client")
        else:
            await ctx.send("Messages.not_connected")
        pass


class SoundBoard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Initialized modules.audio.SoundBoard")

    @commands.command(name="rickroll", aliases=["rr"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def _rickroll(self, ctx):
        if not ctx.voice_client:
            if not ctx.voice_client:
                if ctx.author.voice and ctx.author.voice.channel:

                    destination = ctx.author.voice.channel

                    try:
                        await destination.connect()
                        await ctx.send(Messages.join + destination.name)
                        print("<INFO> Joined channel " + destination.name + "#" + str(destination.id))

                    except:
                        print("<ERROR> Error occurred while joining " + destination.name + "#" + str(destination.id))
                        await ctx.send(Messages.join_error)
                else:
                    await ctx.send(Messages.join_error)
                    return
        elif ctx.voice_client.is_playing:
            await ctx.send("Messages.busy")
        # try:
        with youtube_dl.YoutubeDL(YTDL_OPTIONS) as ytdl:
            url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstleyVEVO"
            rr = ytdl.extract_info(url, download=False)
            ctx.voice_client.play(FFmpegPCMAudio(rr["formats"][0]["url"], **FFMPEG_OPTIONS))

        # except:
        #     await ctx.send("I'm busy!")

    pass


class PlayQueue(object):

    def __init__(self):
        self.queue = Queue()
        self.ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)
        pass

    async def add(self, ctx, what: str):
        if what.startswith("https://www.youtube.com/watch?v=") or what.startswith("https://youtu.be/"):
            # video = pafy.new(play)
            # bestsource = video.getbestaudio()
            # playable = bestsource.url

            song = self.ytdl.extract_info(what, download=False)
            # self.queue.put(song)
            print("Added to queue: " + song["title"])
            await ctx.send("Added to queue: `" + song["title"] + " [" + str(
                datetime.timedelta(seconds=round(song["duration"]))) + "]`")

        elif what.startswith("https://www.youtube.com/playlist?list="):
            songs = self.ytdl.extract_info(what, download=False)["entries"]

            for song in songs:
                self.queue.put(song)
                print("Added to queue: " + song["title"])
                await ctx.send("Added to queue: `" + song["title"] + " [" + str(
                    datetime.timedelta(seconds=round(song["duration"]))) + "]`")

        else:

            results = self.ytdl.extract_info(f"ytsearch:{what}", download=False)
            song = results["entries"][0]
            self.queue.put(song)
            # print(str(song))
            print("Added to queue: " + song["title"])
            await ctx.send("Added to queue: `" + song["title"] + " [" + str(
                datetime.timedelta(seconds=round(song["duration"]))) + "]`")

        pass

    def get(self, _block: bool, _timeout: int):
        try:
            return self.queue.get(block=_block, timeout=_timeout)
        except _queue.Empty:
            raise _queue.Empty()

    def empty(self):
        return self.queue.empty()

    def remove(self):
        return self.queue.get()


class MusicPlayer(object):
    @tasks.loop(seconds=5, count=None)
    async def play_next(self):
        if not self.voice_client.is_playing() and not self.voice_client.is_paused() and not self.anything_in_queue.is_running():
            self.anything_in_queue.start()
        pass

    @play_next.after_loop
    async def after_play_next(self):
        self.anything_in_queue.stop()

    @tasks.loop(seconds=5, count=36)
    async def anything_in_queue(self):
        if not self.queue.empty():
            self.next()
            self.anything_in_queue.stop()
        pass

    @anything_in_queue.after_loop
    async def after_anything_in_queue(self):
        if not self.voice_client.is_playing():
            self.destroy = True
        pass

    def __init__(self, key: str, voice_client: VoiceClient):
        self.voice_client = voice_client
        self.queue = PlayQueue()
        self.now_playing = None
        self.loop = False
        self.key = key
        self.destroy = False
        self.play_next.start()

        pass

    def __del__(self):
        self.play_next.stop()

    async def play(self, ctx, what: str):

        await self.queue.add(ctx, what)
        # print("Added to queue: " + str(what))
        # print(str(self.queue))
        # if not self.voice_client.is_playing():
        #     # ctx.send("Added to queue: "+ str(what))
        #     self.next()
        # if not self.play_next.is_running():
        #     self.play_next.start()

    def next(self):

        try:
            print("Is queue empty:" + str(self.queue.empty()))
            song = self.queue.get(False, 1)

        except _queue.Empty:
            self.destroy = True
            print("chyba")
            return
        self.now_playing = song

        self.voice_client.play(FFmpegPCMAudio(song["formats"][0]["url"], **FFMPEG_OPTIONS)
                               # , after=lambda e: self.next()
                               )

        if self.loop is True:
            self.queue.put(song)
        pass

    async def pause(self):
        await self.voice_client.pause()

        pass

    async def skip(self):
        self.voice_client.stop()
        self.next()
        pass

    pass


class Players(dict):
    def __init__(self):
        self = dict
        pass

    def add(self, key, value: MusicPlayer):
        self[key] = value
        pass

    def removekey(self, key):
        print("Removed key: " + key)
        r = self[key]
        del r

    pass
