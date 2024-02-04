import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from gtts import gTTS
import asyncio

logger = logging.getLogger("my_bot")
logger.setLevel(logging.INFO)

# Create a handler to log to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.info("Loading variables...")
load_dotenv()

intents = discord.Intents.all()
intents.messages = True
intents.guilds = True
intents.voice_states = True


client = commands.Bot(command_prefix="$", intents=intents)

# Dictionary to store active voice channels and their timers
active_voice_channels = {}

async def disconnect_after_timeout(channel):
    try:
        # Disconnect from the voice channel after 5 minutes of inactivity
        await asyncio.sleep(300)  # 300 seconds = 5 minutes

        # Check if there have been no new messages during the timeout period
        if channel not in active_voice_channels or not active_voice_channels[channel]['timer'].done():
            voice_channel = active_voice_channels[channel]['voice_channel']
            await voice_channel.disconnect()
            del active_voice_channels[channel]
            logging.info(f"Bot disconnected from {channel}")
    except asyncio.CancelledError:
        logging.info(f"Timer cancelled for {channel}")

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
            active_voice_channels[channel] = {
                'voice_channel': voice_channel,
                'timer': None  # Initialize timer as None
            }

            voice_channel.play(discord.FFmpegPCMAudio('tts_message.mp3'), after=lambda e: print('done', e))

            # Wait for the TTS message to finish playing
            while voice_channel.is_playing():
                await asyncio.sleep(1)

            # Start the timer after the TTS message finishes playing
            active_voice_channels[channel]['timer'] = asyncio.create_task(disconnect_after_timeout(channel))
        else:
            # Bot is already connected to the channel, just play the new TTS message
            tts = gTTS(text=message.content, lang='en')
            tts.save('tts_message.mp3')

            active_voice_channels[channel]['voice_channel'].play(discord.FFmpegPCMAudio('tts_message.mp3'),
                                                                after=lambda e: print('done', e))
            # Reset the timer for the channel since a new message has been received
            active_voice_channels[channel]['timer'].cancel()
            active_voice_channels[channel]['timer'] = asyncio.create_task(disconnect_after_timeout(channel))
    else:
        #await message.channel.send("You need to be in a voice channel to use this command.")
        logging.info(':(')



client.run(os.getenv("DISCORD_TOKEN"))

