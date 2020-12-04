import traceback
from pathlib import Path
import logging
import os

import discord
from discord.ext import commands

logger = logging.getLogger(__file__)

bot = commands.Bot(command_prefix=commands.when_mentioned_or(("?")), intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("The bot is ready")


for file in Path(__file__).parent.glob("cog/*.py"):
    if file.stem != "__init__":
        extension = ".".join(file.parts[:-1] + (file.stem,))
        try:
            bot.load_extension(extension)
        except Exception:
            print(f"Error while loading extension {extension}")
            print(traceback.format_exc())
        else:
            print(f"Loaded : {extension}")
            pass

bot.run(os.environ["TOKEN"])
