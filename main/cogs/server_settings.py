import discord
from discord.ext import commands
import controllers.db as db
import resources.const as const
import resources.bot_functions as bot_functions
import models.models as models

class ServerSettings(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
   
    #roleToPing - komenda do ustawiania roli do pingowania przy wysylaniu glosowania
    @commands.hybrid_command(name="role_to_ping",with_app_command=True, description = "Set role that bot pings in voting message")
    @commands.has_permissions(administrator = True)
    async def roleToPing(self, ctx, role:discord.Role= None):
        if role.name == '@everyone': #jezeli 'everyone' to nie ma id wiec zapisujemy str
            db.insertQuery(db.updateServerRole(ctx.message.guild.id, "everyone"))
        else:
            db.insertQuery(db.updateServerRole(ctx.message.guild.id, role.id)) 
        await ctx.send(embed = bot_functions.f_embed("Success ✅", "Role has been set successfully", const.color_admin),ephemeral=True)

    #disable_role_to_ping - wylacznie pingowania roli
    @commands.hybrid_command(name="disable_role_to_ping",with_app_command=True, description = "Disable role that bot pings in voting message")  
    @commands.has_permissions(administrator = True)
    async def disableRoleToPing(self,ctx):
        db.insertQuery(db.updateServerRole(ctx.message.guild.id,"None"))
        await ctx.send(embed = bot_functions.f_embed("Success ✅", "Role has been disabled successfully", const.color_admin),ephemeral=True)

    #set_channel - koemnda do wybrania kanalu na ktory ma wyslac glosowanie (stare config)
    @commands.hybrid_command(name="set_channel",with_app_command=True, description = "Use it to set voting channel")
    @commands.has_permissions(administrator = True)
    async def setChannel(self,ctx, channel:discord.channel.TextChannel):
        db.insertQuery(models.Server(ctx.message.guild.id,ctx.message.guild.name,channel.id).toDbServers()) 
        await ctx.send(embed = bot_functions.f_embed("Success ✅", "Channel has been set successfully", const.color_admin),ephemeral=True)

async def setup(bot):
    await bot.add_cog(ServerSettings(bot))