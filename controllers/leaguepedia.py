import mwclient
import json
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import controllers.db as db
import models.models as models
import resources.const as const

site = mwclient.Site('lol.fandom.com', path='/')

#response od leaguepedia api
def leaguepediaResponse(tables,fields,limit='max',where=None,order_by=None,format='json'):
    try:
        response = site.api('cargoquery',
        limit = limit,
        tables = tables,
        fields = fields,
        where = where,
        order_by = order_by,  
        format = format
        )
        return json.loads(json.dumps(response)) #zwrocenie json zamiast orderedDict
    except Exception as err:
        return err
    
def constructMatches():
    decoded = leaguepediaResponse('MatchSchedule','Team1,Team2,Winner,MatchDay,Tab,IsReschedulable, DateTime_UTC ',where="OverviewPage = 'LEC/2023 Season/Spring Season'",order_by='DateTime_UTC')
    last_match_id_query = "SELECT MAX(match_id) FROM Matches;" #query zwracajace id ostatniego wpisanego meczu
    last_match_id = db.selectQuery(last_match_id_query)[0][0] #zwraca tupla w liscie [(n,)] wiec [0][0] zeby dostac numer
    
    if last_match_id == None: #jezeli nie ma jeszcze nic w tabeli
        last_match_id=0

    #dodawanie meczy ktorych jeszcze nie ma
    for i in range(last_match_id,len(decoded['cargoquery'])): #przejscie po wszystkich meczach, len(decoded['cargoquery']) - ilosc meczy
        if decoded['cargoquery'][i]['title']['Tab']!='Tiebreakers':
            match = models.Match(
                i,
                decoded['cargoquery'][i]['title']['Team1'],
                decoded['cargoquery'][i]['title']['Team2'],
                decoded['cargoquery'][i]['title']['Winner'],
                decoded['cargoquery'][i]['title']['MatchDay'],
                decoded['cargoquery'][i]['title']['Tab'][5:],
                decoded['cargoquery'][i]['title']['IsReschedulable'],
                decoded['cargoquery'][i]['title']['DateTime UTC']
            )
            if match.is_reschedulable != True and match.team_1 != 'TBD'and match.team_2 != 'TBD': #sprawdzamy czy kolejnosc sie moze zmienic i czy teamy juz sa wpisane
                db.insertQuery(match.toDbMatches()) #insert into nasza baza danych poprawnego meczu

#isMatchWinner sprawdza czy w danym meczy jest juz wygrany
def isMatchWinner(match):
    decoded = leaguepediaResponse('MatchSchedule','Winner',where=f"OverviewPage = 'LEC/2023 Season/Spring Season' AND MatchDay = '{match.match_day}' AND Tab = 'Week {match.match_week}' AND Team1 = '{match.team_1}' AND Team2 = '{match.team_2}'",order_by='DateTime_UTC')
    return decoded['cargoquery'][0]['title']['Winner'] != None, decoded['cargoquery'][0]['title']['Winner']

#standings zwraca slownik z tabela
def standings():
    decoded = leaguepediaResponse('Standings','Team,Place,Streak,StreakDirection,N',where="OverviewPage = 'LEC/2023 Season/Spring Season'",order_by='N')
    standings ={}
    for team in decoded['cargoquery']:
        standings[team['title']['Team']] = {'place':team['title']['Place'],'streak':team['title']['Streak'],'streak_direction':team['title']['StreakDirection'],'ordered_by':team['title']['N']}
    #standings = {team:{place:x,streak:x,streak_direction:x,ordered_by:x}}
    return standings

#sciaganie championow z API
def getChampions():
    decoded = leaguepediaResponse('Champions','Name')
    champions=[]
    for champion in decoded['cargoquery']:
        champions.append(champion['title']['Name'])
    return champions

#sciaganie odpowiednich playerow z teamow z API
def getPlayers():
    teams=""
    for team in const.dict_long_team:
        teams+=f"'{team}',"
    decoded = leaguepediaResponse('Players','ID',where=f"Team IN ({teams[:-1]}) AND IsSubstitute = 0  AND Role IN ('Support', 'Bot','Mid','Jungle','Top') AND IsRetired = 0",order_by="Team")
    players=[]
    for player in decoded['cargoquery']:
        players.append(player['title']['ID'])
    return players

def checkMatches():
    decoded = leaguepediaResponse('MatchSchedule','Team1,Team2,Winner,MatchDay,Tab,IsReschedulable, DateTime_UTC ',where="OverviewPage = 'LEC/2023 Season/Spring Season'",order_by='DateTime_UTC')
    last_match_id_query = "SELECT MAX(match_id) FROM Matches;" #query zwracajace id ostatniego wpisanego meczu

    matchApi = []
    #dodawanie meczy ktorych jeszcze nie ma
    for i in range(len(decoded['cargoquery'])): #przejscie po wszystkich meczach, len(decoded['cargoquery']) - ilosc meczy
        if decoded['cargoquery'][i]['title']['Tab']!='Tiebreakers':
            matchApi.append( models.Match(
                i+1,
                decoded['cargoquery'][i]['title']['Team1'],
                decoded['cargoquery'][i]['title']['Team2'],
                decoded['cargoquery'][i]['title']['Winner'],
                decoded['cargoquery'][i]['title']['MatchDay'],
                decoded['cargoquery'][i]['title']['Tab'][5:],
                decoded['cargoquery'][i]['title']['IsReschedulable'],
                decoded['cargoquery'][i]['title']['DateTime UTC']
            ))
    matchDb = db.getAllMatches()

    for i, j in zip(matchApi, matchDb):

        if i.match_id == j.match_id and (i.team_1 != j.team_1 or i.team_2 !=j.team_2):
            return True
    return False