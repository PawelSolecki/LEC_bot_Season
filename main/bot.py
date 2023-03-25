from async_timeout import asyncio
import discord
from discord.ext import commands
from datetime import date, datetime
import os
import sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import resources.const as const
import controllers.leaguepedia as leaguepedia
import resources.secret_file as secret

intents = discord.Intents.default()

intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.members = True

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix=">",intents=intents,help_command=None)
TOKEN = secret.bot_token

# @tasks.loop(hours=1.0)
# async def matchesRefresh():
#     leaguepedia.getMatches()

# db.insertBonuses()
#leaguepedia.constructMatches()
# print("This file full path (following symlinks)")
# full_path = os.path.realpath(__file__)
# print(full_path + "\n")
path_to_cog="cogs"
async def load_all_cogs():
    for filename in os.listdir(path_to_cog):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

async def main():
    const.players = leaguepedia.getPlayers()
    const.players_lower = [i.lower() for i in const.players]
    const.champions = leaguepedia.getChampions()
    const.champions_lower = [i.lower() for i in const.champions]
    await load_all_cogs()
    await bot.start(TOKEN)

asyncio.run(main())

#TODO 
#bonusy :) (zadanie dla Senio Java Developer Mamsym Borodulia, chuja tam, zrobilismy)
#-----------------

#TODO v2
#komentarze (+ zweryfikowac komentarze w accuracy)

#stowrzyc drugi serwer i postesowac na 2 na raz

#odległe plany:
#help nawet jak nie ma serwera

#https://trello.com/invite/b/eEE9Yox0/ATTIf26a594eb07fbffa57cc1e12cb46b56238A04150/lecbot

#komendy
# 1. help+
# 2. points + 
# 3. config +
# 4. rolePing +
# 5. helpVote +
# 6. bonus + 
# 7. bonusAnswer +
# 8. helpBonus +
# 9. schedule +
# 10. bonusReset + 
# 11. bonusAvailable  +
# 12. bonusON +
# 13. % dobrych odpowiedzi +
# 14. table +
# 15. feedback (modal to okienko) +

#komendy kategorie
# bot_owners
# server_settngs
# help
# bonus
# common

# Hi, the bot is still in first version actually. It may have a few bugs and not works perfectly. 
# For now I would prefer to run it on one server and to fix possible issues, but at spring split I would be so happy to share it. 

#---Pytanie czy mozemy kumus udostepnic bota, nasza odpowiedz---
# Hello, My name is Rajesh. I'm from IT support department. Can you descibe your problem at first? 
# Please determine how critical is this problem for your bisnes in 1 to 10 scale. I tower in your honest.
# We will contact with you in 24 hours.
# Thank you from the mountain.
