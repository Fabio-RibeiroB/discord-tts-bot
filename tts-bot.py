import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import csv
import discord
from discord.ext import commands
from gtts import gTTS
import asyncio

logger = logging.getLogger("my_bot")
logger.setLevel(logging.INFO)

# Create a handler to log to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
# Create a formatter for the log messages
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Add the formatter to the console handler
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)
logger.info("Loading variables...")

load_dotenv()

intents = discord.Intents.all()
intents.messages = True

client = commands.Bot(command_prefix="$", intents=intents)

# Dictionary to store active voice channels and their timers
active_voice_channels = {}

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    # Ignore messages from the bot itself to avoid infinite loops
    if message.author == client.user:
        return

    # Check if the message is from a user in a voice channel
    if message.author.voice and message.author.voice.channel:
        # Join the voice channel only if the bot is not already connected
        channel = message.author.voice.channel

        if channel not in active_voice_channels:
            # Create a TTS message using gTTS
            tts = gTTS(text=message.content, lang='en')
            tts.save('tts_message.mp3')

            # Play the TTS message
            voice_channel = await channel.connect()
            active_voice_channels[channel] = voice_channel  # Add the channel to active_voice_channels

            voice_channel.play(discord.FFmpegPCMAudio('tts_message.mp3'), after=lambda e: print('done', e))

            # Wait for the TTS message to finish playing
            while voice_channel.is_playing():
                await asyncio.sleep(1)

            # Disconnect from the voice channel after 5 minutes
            await asyncio.sleep(300)  # 300 seconds = 5 minutes
            await voice_channel.disconnect()

            # Remove the channel from active_voice_channels after disconnecting
            del active_voice_channels[channel]
        else:
            await message.channel.send("A TTS message is already playing in the voice channel.")
    else:
        await message.channel.send("You need to be in a voice channel to use this command.")




client.run(os.getenv("DISCORD_TOKEN"))

