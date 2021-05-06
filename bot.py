# coding: utf-8
import traceback
from pathlib import Path
import logging
import os
import sys

import discord
from discord.ext import commands

from utils.my_bot import MyBot

os.chdir(Path(__file__).parent)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    fmt="%(asctime)s %(filename)s:%(lineno)d :: %(levelname)s :: %(name)s :: %(message)s"
)

# set stdout handler
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)
root_logger.addHandler(stdout_handler)


# set stderr handler
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.ERROR)
stderr_handler.setFormatter(formatter)
root_logger.addHandler(stderr_handler)


logger = logging.getLogger(__file__)

bot = MyBot(
    command_prefix=commands.when_mentioned_or("?"), intents=discord.Intents.all()
)


@bot.event
async def on_ready():
    logger.info("The bot is ready")


for file in Path().parent.glob("cog/**/*.py"):
    extension = ".".join(file.parts[:-1] + (file.stem,))
    try:
        bot.load_extension(extension)
    except Exception:
        logger.error(f"Error while loading extension {extension}")
        logger.error(traceback.format_exc())
    else:
        logger.info(f"Loaded {extension}")


bot.run(os.environ["TOKEN"])
