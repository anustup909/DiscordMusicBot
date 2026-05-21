import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Authorized server ID (Leave empty to run on all servers)
ALLOWED_GUILD_ID = os.getenv("ALLOWED_GUILD_ID")
if ALLOWED_GUILD_ID:
    try:
        ALLOWED_GUILD_ID = int(ALLOWED_GUILD_ID)
        print(f"[Info] Bot is locked to Guild ID: {ALLOWED_GUILD_ID}")
    except ValueError:
        print("[Warning] ALLOWED_GUILD_ID in .env is not a valid number. Defaulting to public mode.")
        ALLOWED_GUILD_ID = None

# Initialize static-ffmpeg and get the path
ffmpeg_path = "ffmpeg"  # Fallback to system PATH
print("Initializing FFmpeg binaries...")
try:
    from static_ffmpeg import run
    ffmpeg_path, ffprobe_path = run.get_or_fetch_platform_executables_else_raise()
    print(f"FFmpeg loaded successfully from: {ffmpeg_path}")
except Exception as e:
    print(f"Warning loading static-ffmpeg binaries: {e}")
    print("Will attempt to use system ffmpeg instead.")

# yt-dlp options for streaming best quality audio without downloading files
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # Bind to IPv4 to prevent YouTube IPv6 blockages
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'ios']
        }
    }
}

# FFmpeg options optimized for streaming over the network
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

class GuildMusicState:
    """Manages the music queue and voice client for a specific Discord guild."""
    def __init__(self, bot, guild_id):
        self.bot = bot
        self.guild_id = guild_id
        self.queue = []
        self.current_song = None
        self.voice_client = None

    def is_playing(self):
        return self.voice_client and self.voice_client.is_playing()

    def is_paused(self):
        return self.voice_client and self.voice_client.is_paused()

    def clear(self):
        self.queue.clear()
        self.current_song = None
        if self.voice_client:
            self.voice_client.stop()

    def play_next(self, error=None):
        if error:
            print(f"Playback error in guild {self.guild_id}: {error}")

        if not self.voice_client:
            return

        if len(self.queue) > 0:
            self.current_song = self.queue.pop(0)
            try:
                # Initialize the audio source with the direct URL stream
                source = discord.FFmpegPCMAudio(
                    self.current_song['url'],
                    executable=ffmpeg_path,
                    **FFMPEG_OPTIONS
                )
                
                # We wrap the playing callback to safely execute play_next on completion
                self.voice_client.play(
                    source,
                    after=lambda e: self.bot.loop.call_soon_threadsafe(self.play_next, e)
                )

                # Send Now Playing embed to the respective text channel
                if 'channel' in self.current_song:
                    asyncio.run_coroutine_threadsafe(
                        self.send_now_playing(self.current_song['channel']),
                        self.bot.loop
                    )
            except Exception as e:
                print(f"Error starting playback: {e}")
                if 'channel' in self.current_song:
                    asyncio.run_coroutine_threadsafe(
                        self.current_song['channel'].send(f"❌ Error playing **{self.current_song['title']}**: {e}"),
                        self.bot.loop
                    )
                self.play_next()
        else:
            self.current_song = None

    async def send_now_playing(self, channel):
        if not self.current_song:
            return
        
        embed = discord.Embed(
            title="Now Playing 🎵",
            description=f"[{self.current_song['title']}]({self.current_song['webpage_url']})",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Uploader", value=self.current_song['uploader'], inline=True)
        
        duration_sec = self.current_song['duration']
        minutes = duration_sec // 60
        seconds = duration_sec % 60
        duration_str = f"{minutes:02d}:{seconds:02d}" if duration_sec else "Live Stream"
        embed.add_field(name="Duration", value=duration_str, inline=True)
        
        if self.current_song['thumbnail']:
            embed.set_thumbnail(url=self.current_song['thumbnail'])
            
        await channel.send(embed=embed)


async def extract_song_info(query):
    """Retrieves song information from YouTube using yt-dlp (runs in executor)."""
    loop = asyncio.get_running_loop()
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            # ydl.extract_info is synchronous and blocks, so we run it in a threadpool executor
            data = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False))
        except Exception as e:
            print(f"Error extracting URL '{query}': {e}")
            return None

        if not data:
            return None

        # Check if the result is from a search (list of entries) or direct link
        if 'entries' in data:
            if not data['entries']:
                return None
            data = data['entries'][0]

        return {
            'url': data.get('url'),
            'webpage_url': data.get('webpage_url'),
            'title': data.get('title', 'Unknown Title'),
            'duration': data.get('duration', 0),
            'uploader': data.get('uploader', 'Unknown Uploader'),
            'thumbnail': data.get('thumbnail'),
        }


class MusicBot(commands.Bot):
    """Custom bot subclass to handle startup setup and guild state isolation."""
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.music_states = {}

    def get_music_state(self, guild_id):
        if guild_id not in self.music_states:
            self.music_states[guild_id] = GuildMusicState(self, guild_id)
        return self.music_states[guild_id]

    async def setup_hook(self):
        print("Registering and syncing Slash Commands...")
        if ALLOWED_GUILD_ID:
            try:
                # Syncing specifically to a guild registers commands instantly!
                guild = discord.Object(id=ALLOWED_GUILD_ID)
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                print(f"Successfully synced {len(synced)} slash command(s) to guild {ALLOWED_GUILD_ID} (Instant sync).")
            except Exception as e:
                print(f"Error syncing slash commands to guild: {e}")
        else:
            try:
                synced = await self.tree.sync()
                print(f"Successfully synced {len(synced)} slash command(s) globally.")
            except Exception as e:
                print(f"Error syncing slash commands globally: {e}")


bot = MusicBot()

@bot.event
async def on_ready():
    print("------")
    print(f"Logged in as: {bot.user.name} (ID: {bot.user.id})")
    print(f"Connected to {len(bot.guilds)} server(s).")
    
    # Auto-leave unauthorized guilds on startup
    if ALLOWED_GUILD_ID:
        print(f"Checking guild authorization (Only Guild ID: {ALLOWED_GUILD_ID} is allowed)...")
        for guild in list(bot.guilds):
            if guild.id != ALLOWED_GUILD_ID:
                print(f"Leaving unauthorized guild: {guild.name} (ID: {guild.id})")
                await guild.leave()
                
    print("------")
    print("Bot is ready to play music!")

@bot.event
async def on_guild_join(guild):
    # Auto-leave unauthorized guilds when added
    if ALLOWED_GUILD_ID and guild.id != ALLOWED_GUILD_ID:
        print(f"Leaving unauthorized guild: {guild.name} (ID: {guild.id})")
        await guild.leave()


# ==============================================================================
# MUSIC SLASH COMMANDS
# ==============================================================================

@bot.tree.command(name="join", description="Joins your active voice channel")
async def join(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ You must be in a voice channel to use this command!", ephemeral=True)
        return

    channel = interaction.user.voice.channel
    state = bot.get_music_state(interaction.guild_id)
    
    if interaction.guild.voice_client:
        if interaction.guild.voice_client.channel.id != channel.id:
            await interaction.guild.voice_client.move_to(channel)
            state.voice_client = interaction.guild.voice_client
            await interaction.response.send_message(f"Moved to voice channel: **{channel.name}**")
        else:
            await interaction.response.send_message(f"Already connected to **{channel.name}**", ephemeral=True)
    else:
        try:
            vc = await channel.connect()
            state.voice_client = vc
            await interaction.response.send_message(f"Joined voice channel: **{channel.name}**")
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to connect: {e}", ephemeral=True)


@bot.tree.command(name="play", description="Plays audio from a YouTube link or search query")
@app_commands.describe(query="A YouTube link or words to search (e.g. 'lofi beats')")
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer()  # Defer since downloading info is an API call
    
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.followup.send("❌ You must be in a voice channel to use this command!")
        return

    channel = interaction.user.voice.channel
    state = bot.get_music_state(interaction.guild_id)
    
    # Connect or move to the channel
    if not interaction.guild.voice_client:
        try:
            vc = await channel.connect()
            state.voice_client = vc
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to connect to voice channel: {e}")
            return
    else:
        state.voice_client = interaction.guild.voice_client
        if interaction.guild.voice_client.channel.id != channel.id:
            try:
                await interaction.guild.voice_client.move_to(channel)
            except Exception as e:
                await interaction.followup.send(f"❌ Failed to move to voice channel: {e}")
                return

    # Extract audio information
    song = await extract_song_info(query)
    if not song:
        await interaction.followup.send("❌ Could not find or play that track. Check the search words or link.")
        return
        
    song['channel'] = interaction.channel  # Save text channel reference for the playing callback
    
    if state.is_playing() or state.is_paused():
        state.queue.append(song)
        
        # Send added to queue embed
        embed = discord.Embed(
            title="Added to Queue 📝",
            description=f"[{song['title']}]({song['webpage_url']})",
            color=discord.Color.blue()
        )
        embed.add_field(name="Position", value=f"#{len(state.queue)}", inline=True)
        
        duration_sec = song['duration']
        minutes = duration_sec // 60
        seconds = duration_sec % 60
        duration_str = f"{minutes:02d}:{seconds:02d}" if duration_sec else "Live Stream"
        embed.add_field(name="Duration", value=duration_str, inline=True)
        
        if song['thumbnail']:
            embed.set_thumbnail(url=song['thumbnail'])
            
        await interaction.followup.send(embed=embed)
    else:
        state.queue.append(song)
        await interaction.followup.send(f"🔎 Found **{song['title']}**. Starting playback...")
        state.play_next()


@bot.tree.command(name="pause", description="Pauses the currently playing song")
async def pause(interaction: discord.Interaction):
    state = bot.get_music_state(interaction.guild_id)
    if state.is_playing():
        state.voice_client.pause()
        await interaction.response.send_message("⏸️ Playback paused.")
    else:
        await interaction.response.send_message("❌ Nothing is playing, or it is already paused.", ephemeral=True)


@bot.tree.command(name="resume", description="Resumes paused playback")
async def resume(interaction: discord.Interaction):
    state = bot.get_music_state(interaction.guild_id)
    if state.is_paused():
        state.voice_client.resume()
        await interaction.response.send_message("▶️ Playback resumed.")
    else:
        await interaction.response.send_message("❌ Playback is not paused.", ephemeral=True)


@bot.tree.command(name="skip", description="Skips the current song")
async def skip(interaction: discord.Interaction):
    state = bot.get_music_state(interaction.guild_id)
    if state.is_playing() or state.is_paused():
        state.voice_client.stop()  # Triggers the 'after' callback which calls play_next()
        await interaction.response.send_message("⏭️ Skipped current song.")
    else:
        await interaction.response.send_message("❌ Nothing is playing to skip.", ephemeral=True)


@bot.tree.command(name="stop", description="Stops music, clears the queue, and leaves voice channel")
async def stop(interaction: discord.Interaction):
    state = bot.get_music_state(interaction.guild_id)
    if interaction.guild.voice_client:
        state.clear()
        await interaction.guild.voice_client.disconnect()
        state.voice_client = None
        await interaction.response.send_message("⏹️ Stopped playback, cleared the queue, and disconnected.")
    else:
        await interaction.response.send_message("❌ Bot is not in a voice channel.", ephemeral=True)


@bot.tree.command(name="leave", description="Disconnects the bot from the voice channel")
async def leave(interaction: discord.Interaction):
    # Reuse /stop command handler
    await stop.callback(interaction)


@bot.tree.command(name="queue", description="Displays the current songs in the queue")
async def show_queue(interaction: discord.Interaction):
    state = bot.get_music_state(interaction.guild_id)
    if not state.queue and not state.current_song:
        await interaction.response.send_message("❌ The queue is empty and nothing is currently playing.")
        return

    embed = discord.Embed(title="Music Queue 🎵", color=discord.Color.purple())
    
    if state.current_song:
        embed.description = f"**Currently Playing:** [{state.current_song['title']}]({state.current_song['webpage_url']})"
    
    if state.queue:
        queue_list = []
        for i, song in enumerate(state.queue[:10], start=1):
            duration_sec = song['duration']
            minutes = duration_sec // 60
            seconds = duration_sec % 60
            duration_str = f"{minutes:02d}:{seconds:02d}" if duration_sec else "Live Stream"
            queue_list.append(f"`{i}.` [{song['title']}]({song['webpage_url']}) - `{duration_str}`")
        
        queue_text = "\n".join(queue_list)
        if len(state.queue) > 10:
            queue_text += f"\n*...and {len(state.queue) - 10} more song(s) in queue.*"
        embed.add_field(name="Up Next:", value=queue_text, inline=False)
    else:
        embed.add_field(name="Up Next:", value="No songs in queue. Add songs with `/play`!", inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="nowplaying", description="Shows the details of the active track")
async def nowplaying(interaction: discord.Interaction):
    state = bot.get_music_state(interaction.guild_id)
    if not state.current_song:
        await interaction.response.send_message("❌ Nothing is playing right now.", ephemeral=True)
        return

    embed = discord.Embed(
        title="Now Playing 🎵",
        description=f"[{state.current_song['title']}]({state.current_song['webpage_url']})",
        color=discord.Color.blurple()
    )
    embed.add_field(name="Uploader", value=state.current_song['uploader'], inline=True)
    
    duration_sec = state.current_song['duration']
    minutes = duration_sec // 60
    seconds = duration_sec % 60
    duration_str = f"{minutes:02d}:{seconds:02d}" if duration_sec else "Live Stream"
    embed.add_field(name="Duration", value=duration_str, inline=True)
    
    if state.current_song['thumbnail']:
        embed.set_thumbnail(url=state.current_song['thumbnail'])

    await interaction.response.send_message(embed=embed)


# ==============================================================================
# MAIN ENTRY
# ==============================================================================

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables or .env file.")
        print("Please check your .env file and ensure the token is correctly specified.")
        exit(1)
        
    try:
        bot.run(DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        print("Error: The provided DISCORD_TOKEN is invalid. Please check your token.")
    except Exception as e:
        print(f"An error occurred while starting the bot: {e}")
