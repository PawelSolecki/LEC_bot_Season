from datetime import date
import discord
from discord.ext import commands
from discord import app_commands

import controllers.db as db
import resources.bot_functions as bot_functions
import resources.const as const

from discord.ext.commands import MissingPermissions

import models.models as models
from discord.ext import commands
from datetime import datetime

class Bonus(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
   
    #wlaczenie lub wylaczenie bonusu na serwerze (tylko dla administratorow)
    @commands.hybrid_command(name="bonus_change_state",with_app_command=True,description = "Turn on/off bonus on server")
    @commands.has_permissions(administrator = True)
    async def bonusChangeState(self, ctx, state="ON/OFF"):
        if state.lower() == "on":
            db.updateServerBonusStatus(ctx.guild.id,True)
            await ctx.reply(embed = bot_functions.f_embed("Success ✅", "Bonus has been turned on successfully", const.color_admin))
        elif state.lower() == "off":
            db.updateServerBonusStatus(ctx.guild.id,False)
            await ctx.reply(embed = bot_functions.f_embed("Success ✅", "Bonus has been turned on successfully", const.color_admin))
        else:
            await ctx.reply(embed = bot_functions.f_embed("Error 🤖", "Possible options\n\n**ON** for turning on\n**OFF** for turning off", const.color_red))
    
    #blad w momencie braku permisji
    @bonusChangeState.error
    async def bonusChangeStateError(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.reply(embed = bot_functions.f_embed("Error 🤖","You do not have permissions to execute that command",const.color_red))

    #bonus - komenda do glosowania na bonus
    @commands.hybrid_command(name="bonus",with_app_command=True,description = "Vote for bonus!")
    async def bonus(self, ctx, vote:str):
        print(1)
        if db.getServerById(ctx.guild.id).is_bonus == 0:#jezli bonus wylaczony na serwerze
            await ctx.reply(embed = bot_functions.f_embed("We have a problem 🤖","Bonuses are disabled on this server",const.color_red), ephemeral=True)
            return
        if datetime.now().hour >= 18:#jezli czas na glosowanie minął
            await ctx.reply(embed = bot_functions.f_embed("We have a problem 🤖","The voting time has gone", const.color_red), ephemeral=True)
            return
            
        db.createUser(ctx.author)#tworzymy usera
        user_vote =[]
        user_vote.append(vote)
        today = date.today()
        #today = '2023-01-21' # na czas testow 
        
        bonus_details = db.getServerTodayBonus(ctx.guild.id,today) #[0] - bonus_id, [1] - available_answers(bonus_answer),[2]- bonus-description
        if (vote.lower() in bonus_details[1]) or (bonus_details[1]==["number"] and vote.isdigit()):#jezeli glos jest w bonus_available
            if db.insertBonusVote(db.getUserIdFromUsers(ctx.guild.id, ctx.author.id),bonus_details[0], user_vote):#dodajemy glos do db chyba ze glosowal
                await ctx.reply(embed = bot_functions.f_embed("Success ✅",f"**Today bonus:**\n{bonus_details[2]}\n\n**Your vote:**\n{vote}",const.color_white,"To reset your bonus vote use 'bonus_reset' command"), ephemeral=True)
            else:
                await ctx.reply(embed = bot_functions.f_embed("You have already voted 🤖", "Reset your bonus votes to vote again.", const.color_red), ephemeral=True)
        else: #dal bonus ktorego nie ma w available wiec wysylmy availavble
            await ctx.reply(embed = bot_functions.f_embed("Your answer is not in today's bonus available answers 🤖", f"Vote again with answers from today's bonus available answers:\n {bot_functions.availableBonusAnswer(bonus_details[1])}", const.color_red), ephemeral=True)
    
    #bonusReset - komenda sluzaca do resetowania glosow na bonus
    @commands.hybrid_command(name="bonus_reset",with_app_command=True,description = "Reset your bonus votes!")
    async def bonusReset(self,ctx):
        if db.getServerById(ctx.guild.id).is_bonus == 0: #sprawdzenie czy bonus jest wlaczony na serverze
            await ctx.reply(embed = bot_functions.f_embed("We have a problem 🤖","Bonuses are disabled on this server",const.color_red), ephemeral=True)
            return
        if datetime.now().hour >= 18: #sprawdzenie czy nie zakonczyl sie czas na glosowanie
            await ctx.reply(embed = bot_functions.f_embed("We have a problem 🤖","The voting time has gone", const.color_red), ephemeral=True)
            return
        today = date.today()
        #today = '2023-01-21'
        db.deleteBonus(db.getUserIdFromUsers(ctx.guild.id, ctx.author.id), db.getServerTodayBonus(ctx.guild.id, today)[0]) #usuniecie z bazy bonusu usera
        await ctx.reply(embed = bot_functions.f_embed("Your votes have been reset ✅","You can vote again!", const.color_white), ephemeral=True)

    #bonusAnswer - komenda do ustelania poprawnych odp do dzisejszego bonusu
    @app_commands.command(name="bonus_answer",description = "Command for admins to set bonus's correct answers")
    @app_commands.checks.has_permissions(administrator = True)
    async def bonusAnswer(self,interaction:discord.Interaction):
        if db.getServerById(interaction.guild.id).is_bonus == 0:#jezli bonus wylaczony to informujemy
            await interaction.response.send_message(embed = bot_functions.f_embed("We have a problem 🤖","Bonuses are disabled on this server",const.color_red), ephemeral=True)
            return
        await interaction.response.send_modal(models.BonusAnswerModal(bot = self.bot))
    
    @bonusAnswer.error#blad permisji
    async def bonusAnswerError(self, interaction, error):
       if isinstance(error, app_commands.MissingPermissions):
           await interaction.response.send_message(embed = bot_functions.f_embed("Error 🤖","You do not have permissions to execute that command",const.color_red), ephemeral=True)

    #bonusAvaiable - komenda do wyswietlania dostepnych odpowiedzi na bonus
    @commands.hybrid_command(name="bonus_available",description= "See available answers for today bonus")
    async def bonusAvailable(self,ctx):
        if db.getServerById(ctx.guild.id).is_bonus == 0: #sprawdzenie czy bonus jest wlaczony na serverze
            await ctx.reply(embed = bot_functions.f_embed("We have a problem 🤖","Bonuses are disabled on this server",const.color_red), ephemeral=True)
            return
        today = date.today()
        #today = '2023-03-11'
        bonus_details = db.getServerTodayBonus(ctx.guild.id,today) #wyciagniecie odpowiedzi na bonus z bazy
        await ctx.reply(embed = bot_functions.f_embed("Available for today bonus:", bot_functions.availableBonusAnswer(bonus_details[1]) ,const.color_white),ephemeral=True)
        

async def setup(bot):
    await bot.add_cog(Bonus(bot))
