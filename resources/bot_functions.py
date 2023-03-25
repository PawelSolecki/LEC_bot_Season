import os,sys,discord
from discord.ui import View
import models.models as models
import controllers.db as db
import resources.const as const
import controllers.leaguepedia as leaguepedia

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

#createView tworzy buttony na dany mecz
def createView(today):
    view = View(timeout = None)
    todaysMatches = db.getTodaysMatches(today)
    for i in range(5):
        view.add_item(models.TeamButton(f'team_1.{i}',i,todaysMatches[i].team_1_short, todaysMatches[i].match_id, today))
        view.add_item(models.VsButton(i))
        view.add_item(models.TeamButton(f'team_2.{i}',i,todaysMatches[i].team_2_short, todaysMatches[i].match_id, today))
    view.add_item(models.ResetButton('reset',i,'Reset',today))
    return view

#createVotingMessage zwraca embed dolaczany do wiadomosci z glosowaniem
def createVotingMessage(server,is_bonus, week, day, role):
    title = f"\t\tWeek {week} Day {day}"
    description = ""
    roleToPing = None
    if is_bonus:
        bonus = db.setServerBonus(server,week,day)
        description +=f"**Today bonus:** \n{bonus}\n"
    footer = "To vote just click the buttons below"
    if role != 'None': #jezeli jest rola do pingowania
        roleToPing = "Hi "
        if role == 'everyone':
            roleToPing += f"@{role}"
        else:
            roleToPing += f"<@&{role}>"
        roleToPing += " new voting has just dropped!"

    return f_embed(title, description, const.color_basic,footer),roleToPing

#createVoteEmbedMessage zwraca wiadomosc z glosami usera
def createVoteEmbedMessage(member:discord.member,today):
    users_votes = db.getUserVote(member,today)
    message = ""

    for match in db.getTodaysMatches(today): #todays_matches = [team_1_short, team_2_short, match_id]
        if match.team_1_short in users_votes:
            message+=f"**{match.team_1_short}** vs {match.team_2_short}\n" #pogrubiamy mecz (**) na który user głosował
        else:
             message+=f"{match.team_1_short} vs **{match.team_2_short}**\n"
    return f_embed("**Your votes:**",message,const.color_basic)

#createVotingResultEmbed tworzy i zwraca wiadomosc z wynikami glosowania
def createVotingResultEmbed(server ,today):
    match_details = db.getMatchDetails(today) # [0] = week number, [1] = day number
    title = f"\t\tWeek {match_details[0]} Day {match_details[1]}"

    description =  f"**Server votes (total votes: {countVotes(server,today)})"
    if countBonusVotes(server,today) ==0:
        description+="\n\n**"
    else:
        description = description[:-1]
        description+=f"| total votes for bonus: {countBonusVotes(server,today)}):\n\n**"

    results = {} # {match_id:{team_1_short:ilsoc glosow, team_2_short: ilsoc_glosow}} okresla glosy na dany team w danym meczu
    for match in db.getTodaysMatches(today):
        results[match.match_id] = {match.team_1_short:0,match.team_2_short:0}

    users_string_for_query = "" # okreslenie wszystkich userow servera jako string dla sql IN query
    for user in db.getUsersFromServer(server):
        users_string_for_query += f"{user}, "

    for match in results: # przejscie po kazdym meczu i ustalenie liczby glosow na niego
        for team in results[match]:
            results[match][team] = db.getAmountOfVotes(users_string_for_query,team)

    for match in results: # przejscie po kazdym meczu i tworzenie wiadoomosci
        match_votes=[] # ponowne deklarowanie match_votes i match_pints co iteracje dla kazdego meczu 
        match_teams = []
        for team in results[match]:  # przejscie po meczu oraz dodanie teamu i votow odpowiednio do match_teams i match_votes
            match_votes.append(results[match][team])
            match_teams.append(team)

        if match_votes[0]+match_votes[1]==0: # jezeli bylo brak glosow na dany mecz
            description+= f"0% - {match_teams[0]} {10*const.white_square} {match_teams[1]} - 0%\n\n"
        else:
            team_1_votes = match_votes[0]/(match_votes[0]+match_votes[1]) # obliczenie procentu glosow na pierszy team
            description += f"{round(team_1_votes*100)}% - {match_teams[0]} " # dodanie obliczonego procentu i nazwy pierwszej druzyny
            description += f"{int(round(team_1_votes*10)) * const.red_square}" # dodanie odpowiedniej ilosci czerwonych kwadratow
            description += f"{(10 - int(round(team_1_votes*10))) * const.blue_square}" # oblicznie procenta glosow na drugi team przez odjecie od calosci (czytaj 10 bo team_1_votes poczatkowo ulamkiem ktory potem zamieniamy do liczby naturalnej) i dodanie odpowiedniej ilosci niebieskich kwadratow
            description += f" {match_teams[1]} - {100 - round(team_1_votes*100)}%\n\n" # dodanie drugiego teamu i drugich procentow

    return f_embed(title, description, const.color_basic) # zwrocenie gotowego embeda

#createResultsEmbed zwraca embeda z resultami meczy
def createResultsEmbed(matches):
    description = ""
    for match in matches: #przejscie po kazdym meczu, okreslenie winnera i dodanie odpowiedniego description
        match.isWinner()
        if match.winner == match.team_1_short:
            description+=f"**{match.team_1_short}** 1 : 0 **{match.team_2_short}**\n"
        if match.winner == match.team_2_short:
            description+=f"**{match.team_1_short}** 0 : 1 **{match.team_2_short}**\n"
        description+=".......................\n"
    return f_embed("TODAY'S  RESULTS:", description, const.color_admin) #zwrocenie gotowego embeda
 
#f_embed funckja zwraca embed
def f_embed(title, description, color,footer=None):
    embed=discord.Embed(title=title, description=description, color=color)
    embed.set_author(name="LEC_Bot", url="https://twitter.com/LEC_bot", icon_url="https://pbs.twimg.com/profile_images/1611378090298449920/FtZ5m_6N_400x400.jpg")
    embed.set_footer(text=footer)
    return embed
    
def availableBonusAnswer(bonus_details):
    champions_lower = [i.lower().replace("'", "").replace("&amp;", "&").replace(" ", "") for i in const.champions]
    players_lower = [i.lower().replace(" ","").replace("'", "") for i in const.players]
    games = [str(i) for i in const.games]
    games_with_zero = [str(i) for i in const.games_with_zero]
    
    if bonus_details == champions_lower:
        return ", ".join(const.champions)
    elif sorted(bonus_details) == sorted(players_lower):
            return ", ".join(const.players)
    elif bonus_details == const.teams_lower:
        return ", ".join(const.teams)
    elif bonus_details == ['number']:
        return "Number"
    elif bonus_details == games:
        return ", ".join(games)
    elif bonus_details == games_with_zero:
        return ", ".join(games_with_zero)

#countVotes dodajamy do votingMessageResultEmbed zwraca ilosc glosow danego dnia  
def countVotes(server,today):
    matches = db.getTodaysMatches(today)

    match_ids = "" #do zapytania sql
    for match in matches:
        match_ids += f"{match.match_id}, "
    
    query = db.selectQuery(f"""
    SELECT Servers.server_name, COUNT(DISTINCT(Users_votes.user_id)) FROM Users_votes
    INNER JOIN Users ON Users_votes.user_id = Users.user_id 
    INNER JOIN Servers ON Users.discord_server_id = Servers.discord_server_id
    WHERE match_id IN ({match_ids[:-2]}) AND Servers.discord_server_id = '{server.discord_server_id}'  GROUP BY Servers.server_name
    """)#query zwraca voty danego servera na dany dzien
    if query == []:
        return 0
    return query[0][1]

def countBonusVotes(server,today):
    bonus_id = db.getServerTodayBonus(server.discord_server_id, today)[0]
    users=""
    for i in db.getUsersFromServer(server):
        users+=f"{i}, "
    if users =="":
        return 0
    # server_users =  ", ".join(db.getUsersFromServer(server))

    query =db.selectQuery(f"SELECT COUNT(user_id) FROM Users_bonus_votes WHERE bonus_id = {bonus_id} AND user_id IN ({users[:-2]})")
    if query == []:
        return 0
    return query[0][0]