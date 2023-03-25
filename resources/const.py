import os,sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import resources.bot_functions as bot_functions
import controllers.leaguepedia as leaguepedia

dict_shorts_team = {
'Astralis':'AST',
'Excel Esports':'XL',
'Fnatic':'FNC',
'G2 Esports':'G2',
'KOI (Spanish Team)':'KOI',
'KOI':'KOI',
'MAD Lions':'MAD',
'SK Gaming':'SK',
'Team BDS':'BDS',
'Team Heretics':'TH',
'Team Vitality':'VIT',
'Misfits Gaming':"MSF", #do testow 2022
'Rogue (European Team)':'RGE', #do testow 2022
'TBD':'TBD'
}
dict_long_team = {
'Astralis':'Astralis',
'Excel Esports':'Excel',
'Fnatic':'Fnatic',
'G2 Esports':'G2 Esports',
'KOI (Spanish Team)':'KOI',
'KOI':'KOI',
'MAD Lions':'MAD Lions',
'SK Gaming':'SK Gaming',
'Team BDS':'BDS',
'Team Heretics':'Heretics',
'Team Vitality':'Vitality',
'Misfits Gaming':"Misfits", #do testow 2022
'Rogue (European Team)':'Rogue', #do testow 2022
'TBD':'TBD'
}

champions = leaguepedia.getChampions()
champions_lower = [i.lower().replace("'", "").replace("&amp;", "&").replace(" ", "") for i in champions]

players = leaguepedia.getPlayers()
players_lower = [i.lower() for i in players]

#--------czas zamkniecia voringu--------
h = 10
m = 0
color_white = 0xE7E9E9
color_red = 0xDA1E37
color_basic = 0x5FD1BF
color_admin = 0x1F2425

#🟥 🟦 ⬛ 🟫 🟩 🟧 🟪 ⬜ 🟨
red_square = "🟥"
blue_square = "🟦"
white_square = "⬜"
#---------------wiadomosci---------------
reset_embed_message = bot_functions.f_embed("You can vote again!","Your votes have been reset succesfully!",color_red)
already_voted_embed_message = bot_functions.f_embed("We have a problem 🤖","You have already voted for the team. Click Reset button to reset all your votes.",color_red)

#---------------Bonusy---------------

#jak odswiezac champions i players?
number  = ["number"]
games = [1,2,3,4,5]
games_with_zero = [0,1,2,3,4,5]
teams = ["AST","XL","FNC","G2","KOI","MAD","SK","BDS","TH","VIT"]
teams_lower = ["ast","xl","fnc","g2","koi","mad","sk","bds","th","vit"]
b1 = "How many multikills (at least 3) will be today"
b2 = "How many nashors will be killed today"
b3 = "How many elders will be killed today"
b4 = "How many steals will be during todays games (dragons, elders, heralds, nashors)"
b5 = "The longest game"
b6 = "Which team will score the fewest kills today"
b7 = "The shortest game"
b8 = "Which champion will be picked at least 3 times"
b9 = "Which player will have at least 6 kills"
b10 = "How many players will have more than 6 kills today"
b11 = "Which player will have max 2 deaths"
b12 = "The most bloody game"
b13 = "Player who scores 0 kills"
b14 = "Which champion has not beed picked, but will be picked today"
b15 = "Champion, who has already been picked, but will not be seen at today s games"
b16 = "Player who dies at least 5 times"
b17 = "In how matches a dragon soul will be made"
b18 = "Which player will make the most kill today"
b19 = "How many kills will be scored by player with the most kills today"
b20 = "In how many games will both teams make over 10 kills"
b21 = "Which champion will be picked only once today"
b22 = "How many players will have more than 5 deaths today"
b23 = "Which player will do 1st blood"
b24 = "Player with over 350 cs"
bonuses = {
        b1:number,
        b2:number,
        b3:number,
        b4:number,
        b5:games,
        b6:teams_lower,
        b7:games,
        b8:champions_lower,
        b9:players_lower,
        b10:players_lower,
        b11:players_lower,
        b12:games,
        b13:players_lower,
        b14:champions_lower,
        b15:champions_lower,
        b16:players_lower,
        b17:games_with_zero,
        b18:players_lower,
        b19:number,
        b20:games_with_zero,
        b21:champions_lower,
        b22:number,
        b23:players_lower,
        b24:players_lower
}
