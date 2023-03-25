from discord.ext import commands
import resources.const as const
import controllers.leaguepedia as leaguepedia
import controllers.db as db
import resources.bot_functions as bot_functions
class Bot_owners(commands.Cog):
    def __init__(self,bot) :
        self.bot = bot

    @commands.command()
    async def load(self, ctx:commands.Context,cog:str):
         if isOwner(ctx.author.id):
            try:
                await self.bot.load_extension(f"cogs.{cog}")
                await ctx.reply("Cog loaded succesfully")
            except Exception as e:
                await ctx.reply(f"Error {e}")

    @commands.command()
    async def unload(self, ctx:commands.Context,cog:str):
        if isOwner(ctx.author.id):
            try:
                await self.bot.unload_extension(f"cogs.{cog}")
                await ctx.reply("Cog unloaded succesfully")
            except Exception as e:
                await ctx.reply(f"Error {e}")

    @commands.command()
    async def reload(self, ctx:commands.Context,cog:str):
        if isOwner(ctx.author.id):
            try:
                await self.bot.unload_extension(f"cogs.{cog}")
                await self.bot.load_extension(f"cogs.{cog}")
                await ctx.reply("Cog reloaded succesfully")
            except Exception as e:
                await ctx.reply(f"Error {e}")

    #sync - komenda sluzaca do sync komend
    @commands.command()
    async def sync( self,ctx):
        if isOwner(ctx.author.id):
            synced = await self.bot.tree.sync()
            print(f"Synced {len(synced)} commands")	
            print(synced)
        
    # @commands.command()	
    # async def refresh_players(self,ctx):
    #     if isOwner(ctx.author.id):
    #         const.players = leaguepedia.getPlayers()
    #         const.players_lower = [i.lower() for i in const.players] 
    #         await ctx.reply(const.players_lower)

    # @commands.command()	
    # async def refresh_champions(self,ctx):
    #     if isOwner(ctx.author.id):
    #         const.champions = leaguepedia.getChampions()
    #         const.champions_lower = [i.lower() for i in const.champions]    
    #         await ctx.reply(const.champions_lower)

    #construct_matches - komenda do sciagania meczy z API i wpisywania ich do API
    @commands.command()
    async def construct_matches(self,ctx):
        if isOwner(ctx.author.id):
            leaguepedia.constructMatches()

    #construct_bonuses - komenda sluzaca do wpisywania bonusow do bazy
    @commands.command()
    async def construct_bonuses(self,ctx):
        if isOwner(ctx.author.id):
            db.insertBonuses()
        
    #count_vote - komenda do pokazania ile glosow na jakim serwerze
    @commands.command()
    async def count_vote(self,ctx):
        if isOwner(ctx.author.id):
            description = "\n".join(countVotes())
            await ctx.reply(embed = bot_functions.f_embed("Servers' votes",description,const.color_admin))

#sprawdza czy jest user jest bot_owner
def isOwner(user_id):
    if user_id == 486212235086135338 or user_id ==435071659242684418:
        return True
    return False
    
#countVotes zwraca gotowa liste do wstawienia do embeda
def countVotes():
    embed_descriptions = []
    for i in range(9): # 9 bo jest 9 dni
        match_ids = ""
        for j in range(5): # dzien ma 5 meczy
            match_ids+=f"{1+j+i*5}, "

        query = db.selectQuery(f"""
        SELECT Servers.server_name, COUNT(DISTINCT(Users_votes.user_id)) FROM Users_votes
        INNER JOIN Users ON Users_votes.user_id = Users.user_id 
        INNER JOIN Servers ON Users.discord_server_id = Servers.discord_server_id
        WHERE match_id IN ({match_ids[:-2]}) GROUP BY Servers.server_name
        """)#pojebane zapytanie ale dziala

        server_votes_description=""
        for server_votes in query:
            server_votes_description +=f"{server_votes[0]}: {server_votes[1]}\n"#server_votes[0] = nazwa serwera, [1] ilosc glosow
        if server_votes_description!="":
            embed_descriptions.append(f"**Week {i//3+1} Day {i%3+1}**\n{server_votes_description}")#pojebany sposob na wyznaczenie week i day ale tez dziala, dodajemy calego stringa do tabeli
    return embed_descriptions
async def setup(bot):
    await bot.add_cog(Bot_owners(bot))
