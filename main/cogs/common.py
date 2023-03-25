from datetime import date
import discord,os,sys
from discord.ext import commands
from discord import app_commands

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import controllers.db as db
import resources.bot_functions as bot_functions
import resources.const as const
import models.models as models
import controllers.leaguepedia as leaguepedia

class Common(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    #komenda points sluzy do sprawdziania glosow: swoich, kogos innego i wszystkich na serverze
    @commands.hybrid_command(name="points",with_app_command=True, description = "Use it to check server's points!")
    async def points(self, ctx, given_user_from_user : discord.Member = None):
        try:
            
            embeds_array = [] # tablica Pages dla MenuPages
            description = ""
            server = db.getServerById(ctx.guild.id) #okreslenie servera po guild.id wyciagnietym z wiadomosci
            
            if given_user_from_user == None: # w przypadku gdy sama points tzn. >points to given_user rowne jest authorowi wiadomosci
                given_user_from_user = ctx.author.id
            else:                   # inaczej jest rowny jest innemu memberowi servera
                given_user_from_user = given_user_from_user.id
            
            given_user = db.getUserIdFromUsers(ctx.guild.id, given_user_from_user) # znalezienie user_id podanego usera w db
            if given_user == False:
                db.createUser(ctx.author)
                given_user = db.getUserIdFromUsers(ctx.guild.id, given_user_from_user)

            users_points_dict = db.getUsersPointsAndAnswersAmount(server)[0] # pointsy userow dla tego servera
            users_points_dict = dict(sorted(users_points_dict.items(), key=lambda item: item[1],reverse=True)) #posortowanie pointsow na serverze po ilosci punktow malejaco
            given_user_place = list(users_points_dict.keys()).index(given_user) #miejsce podanego uzytkownika
            
            #przechodmimy po dict'cie (posortowanym malejąco) gdzie kluczem jest user_id(z tabeli Users) a kluczem jego punkty
            #i jest numerem iteracji pętli
            #user to klucz w users_points_dict
            for i, user in zip(range(len(users_points_dict)), users_points_dict):
                description += f"{placeSymbol(i)} <@{db.getDiscordUserIdFromUsers(user)}> : {users_points_dict[user]}\n" # dodajemy linijke z miejscem usera (i+1), z db wyciagamy jego discord id, i bierzemy pointsy z dict'a

                if (i+1)%10==0: #10 okresla ilosc linijek (userow) na jedenej stronie wiec jezeli jest 10 konczymy strone
                    description += f"\n{placeSymbol(given_user_place)} <@{db.getDiscordUserIdFromUsers(given_user)}> : {users_points_dict[given_user]}" #dodajemy numer nazwe i punkty usera podanego w komendzie
                    
                    embeds_array.append(bot_functions.f_embed(f"**Points**",description, const.color_basic, footer=f"Page {(i+1)//10} / {len(users_points_dict)//10+1}")) #aktualny numer strony na maksymalna ilosc (aktualny numer nie ma dzielenia // bo if zapewnia podzielnosc) maks strony + 1 bo // ucina jednosci
                    
                    description="" #zerujemy description dla kolejnej strony
            
            if (i+1)%10!=0: #jezeli i+1 po petli nie jest podzielne przez 10 to trzeba dodac ostatnia strone (gdzie bedzie mniej niz 10 linijek)
                description += f"\n{placeSymbol(given_user_place)} <@{db.getDiscordUserIdFromUsers(given_user)}> : {users_points_dict[given_user]}" #tak samo jak wyzej
                embeds_array.append(bot_functions.f_embed(f"**Points**",description, const.color_basic, footer=f"Page {len(users_points_dict)//10+1} / {len(users_points_dict)//10+1}")) #ten page jest ostani

            await models.MenuPages(embeds=embeds_array,user_id=ctx.author.id,givenUserPage=(given_user_place)//10).send(ctx) # wyslanie gotowych MenuPages, #given_user_plave -1 bo page 10 usera = 0
        
        except Exception as e:
            print(e)
   #komenda points2 sluzy do sprawdziania glosow: swoich, kogos innego i wszystkich na serverze
    @commands.hybrid_command(name="points2",with_app_command=True, description = "Use it to check server's points!")
    async def points2(self, ctx, given_user_from_user : discord.Member = None):
        try:
            embeds_array = [] # tablica Pages dla MenuPages
            description = ""
            server = db.getServerById(ctx.guild.id) #okreslenie servera po guild.id wyciagnietym z wiadomosci
            
            if given_user_from_user == None: # w przypadku gdy sama points tzn. >points to given_user rowne jest authorowi wiadomosci
                given_user_from_user = ctx.author.id
            else:                   # inaczej jest rowny jest innemu memberowi servera
                given_user_from_user = given_user_from_user.id
            
            given_user = db.getUserIdFromUsers(ctx.guild.id, given_user_from_user) # znalezienie user_id podanego usera w db
            if given_user == False:
                db.createUser(ctx.author)
                given_user = db.getUserIdFromUsers(ctx.guild.id, given_user_from_user)

            users_points_dict = db.getUsersPointsAndAnswersAmount(server)[0] # pointsy userow dla tego servera
            users_points_dict = dict(sorted(users_points_dict.items(), key=lambda item: item[1],reverse=True)) #posortowanie pointsow na serverze po ilosci punktow malejaco
            given_user_place = list(users_points_dict.keys()).index(given_user) #miejsce podanego uzytkownika
            
            #przechodmimy po dict'cie (posortowanym malejąco) gdzie kluczem jest user_id(z tabeli Users) a kluczem jego punkty
            #i jest numerem iteracji pętli
            #user to klucz w users_points_dict
            for i, user in zip(range(len(users_points_dict)), users_points_dict):
                description += f"{placeSymbol(i)} *{db.getUserDiscordName(user)}* : {users_points_dict[user]}\n" # dodajemy linijke z miejscem usera (i+1), z db wyciagamy jego discord id, i bierzemy pointsy z dict'a

                if (i+1)%10==0: #10 okresla ilosc linijek (userow) na jedenej stronie wiec jezeli jest 10 konczymy strone
                    description += f"\n{placeSymbol(given_user_place)} *{db.getUserDiscordName(given_user)}* : {users_points_dict[given_user]}" #dodajemy numer nazwe i punkty usera podanego w komendzie
                    
                    embeds_array.append(bot_functions.f_embed(f"**Points**",description, const.color_basic, footer=f"Page {(i+1)//10} / {len(users_points_dict)//10+1}")) #aktualny numer strony na maksymalna ilosc (aktualny numer nie ma dzielenia // bo if zapewnia podzielnosc) maks strony + 1 bo // ucina jednosci
                    
                    description="" #zerujemy description dla kolejnej strony
            
            if (i+1)%10!=0: #jezeli i+1 po petli nie jest podzielne przez 10 to trzeba dodac ostatnia strone (gdzie bedzie mniej niz 10 linijek)
                description += f"\n{placeSymbol(given_user_place)} *{db.getUserDiscordName(given_user)}* : {users_points_dict[given_user]}" #tak samo jak wyzej
                embeds_array.append(bot_functions.f_embed(f"**Points**",description, const.color_basic, footer=f"Page {len(users_points_dict)//10+1} / {len(users_points_dict)//10+1}")) #ten page jest ostani

            await models.MenuPages(embeds=embeds_array,user_id=ctx.author.id,givenUserPage=(given_user_place)//10).send(ctx) # wyslanie gotowych MenuPages, #given_user_plave -1 bo page 10 usera = 0
        
        except Exception as e:
            print(e)
    @app_commands.command(name="schedule",description = "See games schedule 🗓️")
    async def schedule(self, interaction):
        description="" #opis embeda
        embeds = [] #lista embedow w select'cie
        all_matches = db.getAllMatches() #tabela modeli wszystkich meczy
        
        for i,match in zip(range(len(all_matches)),all_matches): #petla tworzy embedy na mecze, i - numer iteracji petli, match - poszczegolny mecz
            
            if match.winner == 'None': #jezeli mecz nie ma winnnera to dajemy vs
                description += f"**{match.team_1_short}** vs **{match.team_2_short}**\n\n"
            else:
                if match.winner == match.team_1_short: #sprawdzamy kto wygrał i odpowiednia dajemy 1 : 0
                    description+=f"**{match.team_1_short}** 1 : 0 {match.team_2_short}\n\n"
                else:
                    description+=f"{match.team_1_short} 0 : 1 **{match.team_2_short}**\n\n" 
            if (i+1)%5==0:  # dodanie do do listy embedow gotowego embeda gdy jest juz 5 meczy
                embeds.append(bot_functions.f_embed(f"**Week {match.match_week} Day {match.match_day}**", description, const.color_basic)) 
                description = "" #clearownaie description
        await interaction.response.send_message(embed=bot_functions.f_embed('Schedule','choose below',0x555555),view=models.GamesMenu(embeds = embeds),ephemeral=True) #wyslanie embeda z MenuPages
    
    #feedback - komenda sluzaca do wysylania feedbacku
    @app_commands.command(name="feedback",description = "Use it to send to bot owners any problems, ideas or anything else")
    async def feedback(self,interaction:discord.Interaction):
        await interaction.response.send_modal(models.FeedbackModal(bot = self.bot)) 
        
    #KOMENDA DO NAPRAWY
    # @commands.hybrid_command(name="accuracy",with_app_command=True, description = "Use it to check the percentage of correct answers")
    # async def accuracy(self, ctx, given_user_from_user : discord.Member = None):
    #     embeds_array = [] # tablica Pages dla MenuPages
    #     description = ""
    #     server = db.getServerById(ctx.guild.id) #okreslenie servera po guild.id wyciagnietym z wiadomosci
    #     users_accuracy_dict = {}
        
    #     if given_user_from_user == None: # w przypadku gdy sama points tzn. >points to given_user rowne jest authorowi wiadomosci
    #         given_user_from_user = ctx.author.id
    #     else:                   # inaczej jest rowny jest innemu memberowi servera
    #         given_user_from_user = given_user_from_user.id

    #     given_user = db.getUserIdFromUsers(ctx.guild.id, given_user_from_user) # znalezienie user_id podanego usera w db
    #     if given_user == False:
    #         db.createUser(ctx.author)
    #         given_user = db.getUserIdFromUsers(ctx.guild.id, given_user_from_user)

    #     answersAndAnswersAmount = db.getUsersPointsAndAnswersAmount(server)
    #     users_points_dict = answersAndAnswersAmount[0] # pointsy userow dla tego servera
    #     users_answers_amount_dict = answersAndAnswersAmount[1]
            
    #     for i in users_points_dict:
    #         if users_answers_amount_dict[i]==0:
    #             users_accuracy_dict[i] = 0
    #         else:
    #             users_accuracy_dict[i] = int(users_points_dict[i]/users_answers_amount_dict[i]*100)

        

    #     users_accuracy_dict = dict(sorted(users_accuracy_dict.items(), key=lambda item: item[1],reverse=True)) #posortowanie pointsow na serverze po ilosci punktow malejaco
    #     given_user_place = list(users_accuracy_dict.keys()).index(given_user) #miejsce podanego uzytkownika
    #     #przechodmimy po dict'cie (posortowanym malejąco) gdzie kluczem jest user_id(z tabeli Users) a kluczem jego punkty
    #     #i jest numerem iteracji pętli
    #     #user to klucz w users_points_dict
    #     for i, user in zip(range(len(users_accuracy_dict)), users_accuracy_dict):
    #         description += f"{placeSymbol(i)} <@{db.getDiscordUserIdFromUsers(user)}> : {users_accuracy_dict[user]}%\n" # dodajemy linijke z miejscem usera (i+1), z db wyciagamy jego discord id, i bierzemy pointsy z dict'a

    #         if (i+1)%10==0: #10 okresla ilosc linijek (userow) na jedenej stronie wiec jezeli jest 10 konczymy strone
    #             description += f"\n{placeSymbol(given_user_place)} <@{db.getDiscordUserIdFromUsers(given_user)}> : {users_accuracy_dict[given_user]}%" #dodajemy numer nazwe i punkty usera podanego w komendzie
                
    #             embeds_array.append(bot_functions.f_embed(f"**Users accuracy**",description, const.color_basic, footer=f"Page {(i+1)//10} / {len(users_accuracy_dict)//10+1}")) #aktualny numer strony na maksymalna ilosc (aktualny numer nie ma dzielenia // bo if zapewnia podzielnosc) maks strony + 1 bo // ucina jednosci
                
    #             description="" #zerujemy description dla kolejnej strony
        
    #     if (i+1)%10!=0: #jezeli i+1 po petli nie jest podzielne przez 10 to trzeba dodac ostatnia strone (gdzie bedzie mniej niz 10 linijek)
    #         description += f"\n{placeSymbol(given_user_place)} <@{db.getDiscordUserIdFromUsers(given_user)}> : {users_accuracy_dict[given_user]}%" #tak samo jak wyzej
    #         embeds_array.append(bot_functions.f_embed(f"**Users accuracy**",description, const.color_basic, footer=f"Page {len(users_accuracy_dict)//10+1} / {len(users_accuracy_dict)//10+1}")) #ten page jest ostani

    #     await models.MenuPages(embeds=embeds_array,user_id=ctx.author.id,givenUserPage=(given_user_place)//10).send(ctx) # wyslanie gotowych MenuPages, #given_user_plave -1 bo page 10 usera = 0
    
    #standings - komenda do wyswietlenia obecnej tabeli
    @commands.hybrid_command(name="standings",with_app_command=True,description = "See current standings")
    async def standings(self,ctx):
        standings = leaguepedia.standings()
        description =""
        for team in standings:
            description +=f"{standings[team]['place']}. {const.dict_long_team[team]}"
            if standings[team]['streak_direction'] == 'W':#jezli win streak to ogien
                description+=" 🔥"
                description+=f" {standings[team]['streak']}\n"
            elif standings[team]['streak_direction'] == 'L':#jezli win streak to mrozi
                description += " 🥶"
                description+=f" {standings[team]['streak']}\n"
            else:
                description+=" 🟰\n"
            
        await ctx.reply(embed = bot_functions.f_embed("Standings",description,const.color_basic))

    #my_vote - zwraca votsy zaleznie od day i week, z defoultu jest today
    @commands.hybrid_command(name = "my_votes",with_app_command=True,description="Shows your todays (or previous) votes")
    async def myVotes(self, ctx, week = None, day = None):
        try:#jak ktos nie week i day a dzis nie ma meczy
            if week == None and day == None:#jezeli nie dal dajemy dzisiejsze
                matches = db.getTodaysMatches(date.today())
                week = matches[0].match_week
                day = matches[0].match_day
            if (int(day) <= 0 or int(day) >= 3) and (int(week) <= 0 or int(week) >= 3):
                return
            user_id = db.getUserIdFromUsers(ctx.guild.id,ctx.author.id)
            #sciaganie votow usera z danego dnia i weeeka
            query = db.selectQuery(f"""
            SELECT vote, Matches.team_1_short,Matches.team_2_short FROM Users_votes
            INNER JOIN Matches ON Users_votes.match_id = Matches.match_id
            WHERE user_id = {user_id} AND Matches.match_day = {day} AND Matches.match_week = {week}
            ORDER BY Matches.match_id
            """)
            description = ""
            for match in query: #odpowiednie dodanie teamow do wiadomosci
                if match[0]==match[1]:
                    description += f"**{match[0]}** vs {match[2]}\n"
                elif match[0]==match[2]:
                    description += f"{match[1]} vs **{match[0]}**\n"
                else:
                    description += f"{match[1]} vs {match[2]}\n"
            if db.getServerById(ctx.guild.id).is_bonus==1: #sciaganie bonusu usera z danego dnia i weeka
                query2 = db.selectQuery(f"""
                SELECT vote FROM Users_bonus_votes
                INNER JOIN Bonuses ON Users_bonus_votes.bonus_id = Bonuses.bonus_id
                INNER JOIN Server_bonuses ON Bonuses.bonus_id = Server_bonuses.bonus_id
                WHERE user_id = {user_id} AND Server_bonuses.day = {day} AND Server_bonuses.week = {week}
                """)
                if query2 !=[]: #dodanie sciagnietych bonusow do wiadomosci
                    bonus = str(query2[0][0])[2:-2]
                    description+=f"\n**Your Bonus:**\n{bonus}"
            
            await ctx.reply(embed = bot_functions.f_embed(f"**Your votes week {week} day {day}**",description,const.color_basic),ephemeral=True)
        except:
            None
#------koniec komend--------

#placeSymbol zwraca numer miejsca
def placeSymbol(place): 
    if place == 0: # jezeli pierwsze miejsce
        return "🥇" 
    elif place == 1: # jezeli drugie miejsce
        return "🥈"
    elif place == 2: # jezeli trzecie miejsce
        return "🥉"
    else:           # w przypadku pozostalych miejsc
        return f"**{place+1}.**" 
   
async def setup(bot):
    await bot.add_cog(Common(bot))
