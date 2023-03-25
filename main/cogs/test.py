from datetime import date
import discord,sys,os
from discord.ext import commands
from discord import app_commands

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import controllers.db as db
import resources.bot_functions as bot_functions
import resources.const as const
import models.models as models

class Test(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
   

async def setup(bot):
    await bot.add_cog(Test(bot))