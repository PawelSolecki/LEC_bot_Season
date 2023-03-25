from discord.ext import commands
import controllers.db as db
import resources.bot_functions as bot_functions
import resources.const as const
from discord.ext.commands import MissingPermissions

footer = "'h' means hybrid command (could be use with '/' and '>' prefix)\n's' means slash command (could be use only with '/')"
class Help(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.hybrid_command(name="bonus_help",with_app_command=True,description = "Help for bonus")
    @commands.has_permissions(administrator = True)
    async def bonusHelp(self, ctx):
        if db.getServerById(ctx.guild.id).is_bonus == 0:
            await ctx.reply(embed = bot_functions.f_embed("We have a problem 🤖","Bonuses are disabled on this server",const.color_red), ephemeral=True)
            return
        await ctx.reply(embed = bot_functions.f_embed("Bonus help",
        """
        Every match day has different bonus, which displays at the top of the buttons in voting message
        Each correct answer is worth two point\n
        **'bonus'** (h) command with your answer(s) to vote
        **'bonus_reset'** (h) command to reset your bonus vote
        **'bonus_available'** (h) command to see today bonus available answer(s)
        """,const.color_basic, footer), ephemeral=True)
        await ctx.author.send(embed = bot_functions.f_embed("Bonus help for admins",
        """
        **'bonus_answer'** (s) command to set correct answers for today bonus
        **'bonus_change_state'** (h) command to turn on/off bonuses on server
        """,const.color_admin,footer))

    @bonusHelp.error
    async def bonusHelpError(self, ctx, error):
        if isinstance(error, MissingPermissions):
            if db.getServerById(ctx.guild.id).is_bonus == 0:
                await ctx.reply(embed = bot_functions.f_embed("We have a problem 🤖","Bonuses are disabled on this server",const.color_red), ephemeral=True)
                return
            await ctx.reply(embed = bot_functions.f_embed("Bonus help",
            """
            Every match day has different bonus, which displays at the top of the buttons in voting message\n
            Each correct answer is worth two point\n
            **'bonus'** (h) command with your answer(s) to vote
            **'bonus_reset'** (h) command to reset your bonus vote
            **'bonus_available'** (h) command to see today bonus available answer(s)
            """,const.color_basic,footer), ephemeral=True)

    @commands.hybrid_command(name = "help",with_app_command=True, description= "Help")
    @commands.has_permissions(administrator = True)
    async def help(self, ctx):

        description ="""
        ***Common:***\n
        **'points'** (h) command to check server users' points
        **'accuracy'** (s) command to check server users' accuracy
        **'schedule'** (s) command to check weeks' schedule 
        **'standings'** (h) command to check current standings
        **'feedback'** (s) command to give feedback for bot oweners
        **'my_vote'** (s) command to see your's today vote
        \n***Help***\n
        **'help_vote'** (h) command to discover how to vote
        **'help'** (h) *this message*\n"""
        if db.getServerById(ctx.guild.id).is_bonus == 1:
            description +="""**'bonus_help'** (h) command to discover how to vote for bonus
            \n***Bonuses:***\n
            **'bonus'** (h) command with your answer(s) to vote
            **'bonus_reset'** (h) command to reset your bonus vote
            **'bonus_available'** (h) command to see today bonus available answer(s)
            """
        description_admin=description
        
        description_admin+="""\n***Admin***\n
        **'role_to_ping'** (h) command to set role to ping in every new voting message
        **'disable_role_to_ping'** (h) command to disable role to ping in every new voting message
        **'set_channel'** (h) command to set channel where new voting message wiil be send
        **'bonus_change_state'** (h) command to turn 'off' or turn on bonus 'on' server (use with off or on parameter)
        """
        await ctx.author.send(embed = bot_functions.f_embed("Help",description_admin,const.color_admin,footer))
        await ctx.reply(embed = bot_functions.f_embed("Help",description,const.color_admin,footer), ephemeral=True)

    @help.error
    async def helpError(self, ctx, error):
        if isinstance(error, MissingPermissions):
            description ="""
            ***Common:***\n
            **'points'** (h) command to check server users' points
            **'accuracy'** (s) command to check server users' accuracy
            **'schedule'** (s) command to check weeks' schedule 
            **'standings'** (h) command to check current standings
            **'feedback'** (s) command to give feedback for bot oweners
            **'my_vote'** (s) command to see your's today vote
            \n***Help***\n
            **'help_vote'** (h) command to discover how to vote
            **'help'** (h) *this message*\n"""
            if db.getServerById(ctx.guild.id).is_bonus == 1:
                description +="""**'bonus_help'** (h) command to discover how to vote for bonus
                \n***Bonuses:***\n
                **'bonus'** (h) command with your answer(s) to vote
                **'bonus_reset'** (h) command to reset your bonus vote
                **'bonus_available'** (h) command to see today bonus available answer(s)
                """
            await ctx.reply(embed = bot_functions.f_embed("Help",description,const.color_basic,footer), ephemeral=True)

    @commands.hybrid_command(name = "help_vote",with_app_command=True, description= "How to vote")   
    async def helpVote(self, ctx):
        await ctx.reply(embed = bot_functions.f_embed("Help vote","""
        You can vote to each team by clicking buttons
        You can reset your votes by clicking 'Reset' button\n
        Each correct answer is worth one point
        Voting starts at 8 (CET) and ends at 18 (CET)
        """,const.color_admin), ephemeral=True)

        
async def setup(bot):
    await bot.add_cog(Help(bot))
