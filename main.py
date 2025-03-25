import discord
from discord.ext import commands
import os
import sys
import tempfile
import zipfile
import shutil
import urllib.request
from dotenv import load_dotenv
import asyncio
from keep_alive import keep_alive

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
# Get the target user from environment variables, with a fallback
TARGET_USER = os.getenv('TARGET_USER', '_mbw9_')

# Set up the bot with command prefix and intents
intents = discord.Intents.default()
intents.message_content = True  # Required for responding to messages
intents.voice_states = True  # Required for voice state updates
bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to track voice clients per guild
voice_clients = {}

# Create a directory for FFmpeg and other resources
if not os.path.exists('bot_resources'):
    os.makedirs('bot_resources')

# Check if the sounds directory exists, create it if it doesn't
if not os.path.exists('sounds'):
    os.makedirs('sounds')

# FFmpeg management
def setup_ffmpeg():
    """Download and set up FFmpeg if it's not already available."""
    global FFMPEG_PATH
    
    # Define the path where we'll store FFmpeg
    ffmpeg_dir = os.path.join(os.getcwd(), 'bot_resources')
    FFMPEG_PATH = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
    
    # Check if FFmpeg already exists
    if os.path.isfile(FFMPEG_PATH):
        print(f"FFmpeg found at: {FFMPEG_PATH}")
        return FFMPEG_PATH
    
    # Try system FFmpeg first
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        print("System FFmpeg is available, using that instead of downloading")
        FFMPEG_PATH = 'ffmpeg'
        return FFMPEG_PATH
    except Exception:
        print("FFmpeg not found on system PATH, will download it...")
    
    # If we're here, we need to download FFmpeg
    try:
        print("Downloading FFmpeg...")
        ffmpeg_url = 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip'
        
        # Create a temporary directory for the download
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the zip file
            zip_path = os.path.join(temp_dir, 'ffmpeg.zip')
            urllib.request.urlretrieve(ffmpeg_url, zip_path)
            
            print("Extracting FFmpeg...")
            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the ffmpeg.exe file
            for root, dirs, files in os.walk(temp_dir):
                if 'ffmpeg.exe' in files:
                    ffmpeg_exe_path = os.path.join(root, 'ffmpeg.exe')
                    # Copy to our resources directory
                    shutil.copy2(ffmpeg_exe_path, FFMPEG_PATH)
                    print(f"FFmpeg set up at: {FFMPEG_PATH}")
                    break
        
        if not os.path.isfile(FFMPEG_PATH):
            raise Exception("Could not find ffmpeg.exe in the downloaded package")
            
        return FFMPEG_PATH
            
    except Exception as e:
        print(f"Error setting up FFmpeg: {e}")
        print("Please install FFmpeg manually and add it to your PATH")
        FFMPEG_PATH = 'ffmpeg'  # Fall back to system PATH
        return FFMPEG_PATH

# Set up FFmpeg path
FFMPEG_PATH = setup_ffmpeg()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    print(f'Bot will follow user: {TARGET_USER}')
    
    # Check if FFmpeg is working
    try:
        import subprocess
        result = subprocess.run([FFMPEG_PATH, '-version'], capture_output=True, text=True)
        print("FFmpeg is available:", FFMPEG_PATH)
    except Exception as e:
        print(f"WARNING: FFmpeg may not be correctly installed: {e}")
        print("Audio playback may not work correctly")

@bot.command(name='hello')
async def hello(ctx):
    """Responds with a hello message"""
    await ctx.send(f'Hello {ctx.author.mention}! I am a Discord bot.')

@bot.command(name='ping')
async def ping(ctx):
    """Check the bot's latency"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! Latency is {latency}ms')

@bot.command(name='leave')
async def leave(ctx):
    """Command to make the bot leave the voice channel"""
    if ctx.guild.id in voice_clients and voice_clients[ctx.guild.id].is_connected():
        await voice_clients[ctx.guild.id].disconnect()
        voice_clients.pop(ctx.guild.id, None)
        await ctx.send("I've left the voice channel!")
    else:
        await ctx.send("I'm not in a voice channel!")

@bot.command(name='stop')
async def stop(ctx):
    """Command to stop playing sound"""
    if ctx.guild.id in voice_clients and voice_clients[ctx.guild.id].is_playing():
        voice_clients[ctx.guild.id].stop()
        await ctx.send("Stopped playing sound!")
    else:
        await ctx.send("I'm not playing anything!")

@bot.event
async def on_voice_state_update(member, before, after):
    # Check if bot was server-muted or deafened
    if member.id == bot.user.id:
        # If bot was server muted
        if not before.mute and after.mute:
            print("Bot was server-muted, attempting to reconnect...")
            guild_id = after.channel.guild.id
            
            # Rejoin to try to clear the mute
            if guild_id in voice_clients and voice_clients[guild_id].is_connected():
                channel = voice_clients[guild_id].channel
                await voice_clients[guild_id].disconnect()
                voice_clients[guild_id] = await channel.connect()
                print("Bot has reconnected to try to clear mute status")
        
        return
    
    # Only track the target user
    if member.name != TARGET_USER:
        return
        
    # If user joined a channel or moved between channels
    if after.channel is not None:
        channel = after.channel
        guild_id = channel.guild.id
        
        print(f'Target user {TARGET_USER} moved to {channel.name}')
        
        # Connect to the voice channel if not already connected
        try:
            # If the bot is already in a voice channel in this guild
            if guild_id in voice_clients and voice_clients[guild_id].is_connected():
                voice_client = voice_clients[guild_id]
                
                # If bot is in a different channel, move to the new one
                if voice_client.channel.id != channel.id:
                    await voice_client.move_to(channel)
            else:
                # Connect to the channel
                voice_client = await channel.connect()
                voice_clients[guild_id] = voice_client
            
            # Play the sound file
            sound_file = 'sounds/sound.mp3'
            
            # Check if the sound file exists
            if not os.path.isfile(sound_file):
                print(f"WARNING: Sound file not found: {sound_file}")
                print(f"Current directory: {os.getcwd()}")
                print(f"Files in sounds directory: {os.listdir('sounds') if os.path.exists('sounds') else 'sounds directory not found'}")
                return
            
            # Play sound (no looping)
            if voice_client.is_playing():
                voice_client.stop()
                
            audio_source = discord.FFmpegPCMAudio(
                sound_file, 
                executable=FFMPEG_PATH
            )
            
            # Function to leave after playing
            def after_playing(error):
                if error:
                    print(f'Player error: {error}')
                
                # Schedule disconnection in the event loop
                asyncio.run_coroutine_threadsafe(
                    disconnect_after_playing(guild_id),
                    bot.loop
                )
            
            voice_client.play(audio_source, after=after_playing)
            print(f"Playing sound: {sound_file}")
                
        except Exception as e:
            print(f"Error in voice channel: {e}")
            import traceback
            traceback.print_exc()
    
    # If the user left all voice channels, leave too
    elif before.channel is not None and after.channel is None:
        guild_id = before.channel.guild.id
        print(f'Target user {TARGET_USER} left all voice channels')
        
        if guild_id in voice_clients and voice_clients[guild_id].is_connected():
            await voice_clients[guild_id].disconnect()
            voice_clients.pop(guild_id, None)

# Function to disconnect after playing
async def disconnect_after_playing(guild_id):
    if guild_id in voice_clients and voice_clients[guild_id].is_connected():
        # Wait a short moment before disconnecting
        await asyncio.sleep(0.5)
        
        if not voice_clients[guild_id].is_playing():
            print(f"Sound finished playing, leaving voice channel in guild {guild_id}")
            await voice_clients[guild_id].disconnect()
            voice_clients.pop(guild_id, None)

# Start the keep_alive server before running the bot
keep_alive()
print("Starting Discord bot...")

# Run the bot with your token
bot.run(TOKEN) 