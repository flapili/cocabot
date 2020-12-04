import traceback
from pathlib import Path
import logging
import os

import discord
from discord.ext import commands

logging.basicConfig(
    level=logging.INFO,
    format="'%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s'",
)

logger = logging.getLogger(__file__)

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(("?")), intents=discord.Intents.all()
)


@bot.event
async def on_ready():
    logger.info("The bot is ready")


for file in Path(__file__).parent.glob("cog/*.py"):
    if file.stem != "__init__":
        extension = ".".join(file.parts[:-1] + (file.stem,))
        try:
            bot.load_extension(extension)
        except Exception:
            logger.error(f"Error while loading extension {extension}")
            logger.error(traceback.format_exc())
        else:
            logger.info(f"Loaded {extension}")


bot.run(os.environ["TOKEN"])
