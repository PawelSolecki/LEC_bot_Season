from datetime import date
import os
import sys
import discord 
from discord.ui import Button

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import controllers.db as db
import resources.bot_functions as bot_functions
import controllers.leaguepedia as leaguepedia
import resources.const as const

class Match:
	def __init__(self, match_id,team_1,team_2,winner,match_day,match_week,is_reschedulable,date):
		self.match_id = match_id
		self.team_1 = team_1
		self.team_1_short = const.dict_shorts_team[self.team_1]
		self.team_2 = team_2
		self.team_2_short = const.dict_shorts_team[self.team_2]
		self.winner = winner
		self.match_day = int(match_day)
		self.match_week = int(match_week)
		self.is_reschedulable = is_reschedulable
		self.date = date
		
	def toDbMatches(self):
		return f"""INSERT INTO Matches (team_1, team_2, team_1_short, team_2_short, winner, match_day, match_week, date) VALUES (
		'{self.team_1}', 
		'{self.team_2}', 
		'{self.team_1_short}', 
		'{self.team_2_short}', 
		'{self.winner}',
		{self.match_day}, 
		{self.match_week}, 
		'{self.date[:-9]}'
		);""" # match_day to w db day
	def isWinner(self):
		match_winner_details = leaguepedia.isMatchWinner(self)
		
		if match_winner_details and match_winner_details[1] == "1":
			self.winner = self.team_1_short
		elif match_winner_details:
			self.winner = self.team_2_short
		db.updateMatchWinner(self)
		return match_winner_details[0]

class Server:
	def __init__(self,discord_server_id,server_name, channel,role_id=None,is_bonus=0,voting_message_id=None):
		self.discord_server_id = discord_server_id
		self.role_id = role_id
		self.server_name = server_name
		self.is_bonus = is_bonus
		self.channel = channel
		self.voting_message_id = voting_message_id
	def toDbServers(self):
		return f"""INSERT INTO Servers (discord_server_id, role_id, server_name, is_bonus, channel) VALUES (
		'{self.discord_server_id}',  
		'{self.role_id}', 
		'{self.server_name}', 
		{self.is_bonus}, 
		'{self.channel}'
		);"""# is_bonus bez cudzyslowia bo to boolean
	def votingMessageIdToDb(self,voting_message_id):
		self.voting_message_id = voting_message_id
		db.insertQuery(f"UPDATE Servers SET voting_message_id = '{voting_message_id}' WHERE discord_server_id = '{self.discord_server_id}'")

class TeamButton(Button):
	def __init__(self, custom_id, row, label, match_id,today):
		super().__init__(label=label, style=discord.ButtonStyle.blurple, custom_id=custom_id, row=row)
		self.id = custom_id
		self.match_id = match_id
		self.today = today
	async def callback (self, interaction):
		
		member = interaction.user
		db.createUser(member) #tworzymy usera jezeli go nie ma
		
		if db.insertVote(member,self.match_id,self.label): #dodajemy glosy, zwraca True jezeli user glosowal juz na mecz
			await interaction.response.send_message(embed = const.already_voted_embed_message,ephemeral=True)
			return
		
		if db.isVoteForAll(member,self.today): #jezli glosowal na wszystkie to wysyla wiadomosc
			await interaction.response.send_message(embed = bot_functions.createVoteEmbedMessage(member, self.today),ephemeral=True)

		try: #to jest tajemnica
			await interaction.response.send_message()
		except:
			None

class VsButton(Button):
	def __init__(self, row):
		super().__init__(label="vs", style=discord.ButtonStyle.grey, disabled = True, row=row)

class ResetButton(Button):
	def __init__(self, custom_id, row, label,today):
		super().__init__(label=label, style=discord.ButtonStyle.red, custom_id=custom_id, row=row)
		self.today = today
	async def callback (self, interaction):
		member = interaction.user
		
		db.deleteVote(member,self.today) #usuniecie vote'ow usera z danego serwera
		
		await interaction.response.send_message(embed=const.reset_embed_message,ephemeral=True)
		
class MenuPages(discord.ui.View):
	async def send(self,ctx):
		try:
			self.message = await ctx.reply(embed=self.embeds[0],view=self,ephemeral=True)
		except Exception as e:
			print(e)
	def __init__(self,embeds,givenUserPage,user_id,timeout=60):
		
		super().__init__(timeout=timeout)
		self.nextButton : discord.ui.Button = MenuButton(label="Next",custom_id="next",row=0,MenuPages=self)
		self.previousButton : discord.ui.Button = MenuButton(label="Previous",custom_id="previous",row=0,MenuPages=self)
		self.jumpToMeButton : discord.ui.Button = MenuButton(label="Jump to you",custom_id="jump",row=0,MenuPages=self)
		self.embeds = embeds
		self.pageAmount = len(embeds)
		self.currentPage = 0
		self.givenUserPage = givenUserPage
		self.previousButton.disabled=True
		self.user_id=user_id
		if len(embeds)==1:
			self.nextButton.disabled=True
		self.add_item(self.previousButton)
		self.add_item(self.nextButton)
		self.add_item(self.jumpToMeButton)
	async def updateMessage(self,custom_id, interaction):
		try:
			if interaction.user.id == self.user_id:
				if custom_id=="next":
					self.currentPage+=1 #zwiekszamy strone
					await self.message.edit(embed=self.embeds[self.currentPage]) #zmieniamy embed na jeden dalszy

					if self.currentPage == self.pageAmount-1: #jezel jest to ostatnia stona (-1 bo dlugosc liczy od 0 )
						self.nextButton.disabled = True #wylaczmy przycisk
						await self.message.edit(view=self)#odswiezamy widok zeby przyciski sie odswiezyly

					if self.previousButton.disabled:#jezeli drugi przycisk byl wylaczony to go wlaczmy 
						self.previousButton.disabled=False
						await self.message.edit(view=self)#odswiezamy widok zeby przyciski sie odswiezyly

				if custom_id=="previous":
					self.currentPage-=1
					await self.message.edit(embed=self.embeds[self.currentPage])

					if self.currentPage == 0:
						self.previousButton.disabled = True
						await self.message.edit(view=self)
						
					if self.nextButton.disabled:
						self.nextButton.disabled = False
						await self.message.edit(view=self)
				if custom_id =="jump":
					self.currentPage = self.givenUserPage
					self.nextButton.disabled = False
					self.previousButton.disabled = False
					if self.currentPage == len(self.embeds)-1:
						self.nextButton.disabled = True
					if self.currentPage == 0:
						self.previousButton.disabled = True
					await self.message.edit(embed=self.embeds[self.currentPage],view=self)
			else:
				await interaction.response.send_message(embed = bot_functions.f_embed("We have a problem 🤖","It's not your message, use 'points' command.",const.color_red),ephemeral=True)
		except Exception as e:
			print(e)

class MenuButton(discord.ui.Button):
	def __init__(self, custom_id, row, label,MenuPages):
		super().__init__(label=label,style=discord.ButtonStyle.blurple, custom_id = custom_id, row = row)
		self.MenuPages = MenuPages
	async def callback(self,interaction):
		try:
			await MenuPages.updateMessage(self.MenuPages,self.custom_id,interaction)
			await interaction.response.send_message()#bez interaction button zwraca blad mimo ze dziala wiec daje mu zeby nic nie robil takto zwraca blad ktory eliminuje try'em
		except Exception as e:
			#print(e)
			None

class Select(discord.ui.Select):
	def __init__(self, embeds):
		self.embeds = embeds
		
		options=[
			discord.SelectOption(label="week 1 day 1",value="w1d1"),
			discord.SelectOption(label="week 1 day 2",value="w1d2"),
			discord.SelectOption(label="week 1 day 3",value="w1d3"),

			discord.SelectOption(label="week 2 day 1",value="w2d1"),
			discord.SelectOption(label="week 2 day 2",value="w2d2"),
			discord.SelectOption(label="week 2 day 3",value="w2d3"),
			
			discord.SelectOption(label="week 3 day 1",value="w3d1"),
			discord.SelectOption(label="week 3 day 2",value="w3d2"),
			discord.SelectOption(label="week 3 day 3",value="w3d3")
		]	
		super().__init__(placeholder="choose match date",options = options)
	async def callback(self,interaction : discord.Interaction):
		if self.values[0] == "w1d1":
			await interaction.response.edit_message(embed=self.embeds[0])
		if self.values[0] == "w1d2":
			await interaction.response.edit_message(embed=self.embeds[1])
		if self.values[0] == "w1d3":
			await interaction.response.edit_message(embed=self.embeds[2])

		if self.values[0] == "w2d1":
			await interaction.response.edit_message(embed=self.embeds[3])
		if self.values[0] == "w2d2":
			await interaction.response.edit_message(embed=self.embeds[4])
		if self.values[0] == "w2d3":
			await interaction.response.edit_message(embed=self.embeds[5])

		if self.values[0] == "w3d1":
			await interaction.response.edit_message(embed=self.embeds[6])
		if self.values[0] == "w3d2":
			await interaction.response.edit_message(embed=self.embeds[7])
		if self.values[0] == "w3d3":
			await interaction.response.edit_message(embed=self.embeds[8])

class GamesMenu(discord.ui.View):
	def __init__(self, *,embeds, timeout=60):
		self.embeds = embeds
		super().__init__(timeout=timeout)
		self.add_item(Select(embeds = self.embeds))
	async def on_timeout(self):
		None #TODO ogarnac wylaczanie select menu po jakims czasie

#klasa do komendy bonus_answer	
class BonusAnswerModal(discord.ui.Modal, title= "Bonus answer"):
	answers = discord.ui.TextInput(label="Enter bonus's correct answers",placeholder="Seperate each answer using semicolon(;)\ne.g. yasuo; yone; caitlyn; jax",style=discord.TextStyle.long)

	def __init__(self, *, bot,title = "Bonus answer", timeout= None, custom_id=""):
		self.bot = bot
		super().__init__(title=title)
		
	#na wyslanie i potwierdzenie
	async def on_submit(self, interaction: discord.Interaction):
		answers = str(self.answers).replace(" ","").split(";") 
		server = db.getServerById(interaction.guild.id)

		today = date.today()
		#today = '2023-01-23' # na czas testow 
		bonus_details = db.getServerTodayBonus(server.discord_server_id,today)

		if db.updatePointsBonus(server, answers, bonus_details) == False:#jezli wprowadzone odpowiedzi nie sa w availavle answers to errow
			await interaction.user.send(embed = bot_functions.f_embed("We have a problem 🤖", f"Available answers for today bonus\n {bot_functions.availableBonusAnswer(bonus_details[1])}",const.color_red))
		else:#wysylamy potwierdzenie
			try:
				await self.bot.get_channel(int(server.channel)).send(embed=bot_functions.f_embed("Correct answer(s) for today bonus:",f"{', '.join(answers)}", const.color_basic))
				description = f"**{', '.join(answers)}**"
				description += db.getMostVotedBonusAnswer(server, today)
				await interaction.user.send(embed = bot_functions.f_embed("Answer(s) you chose as correct for today bonus:", description,const.color_admin))
			except Exception as e:
				print("Bonus Answer error: ",e)

		try: # nawet najstarsi górale nie wiedzą po co i dalczego to tu jest
			await interaction.response.send_message("")
		except:
			None


class FeedbackModal(discord.ui.Modal, title= "Feedback"):
	feedback_title = discord.ui.TextInput(label="Title",placeholder="e.g. problem with 'schedule' command ",style=discord.TextStyle.short)
	category = discord.ui.TextInput(label="Category",placeholder="e.g. bug",style=discord.TextStyle.short)
	description = discord.ui.TextInput(label="Description",placeholder="Place to describe",style=discord.TextStyle.long)

	def __init__(self, *, bot,title = "Feedback", timeout= None, custom_id=""):
		self.bot = bot
		super().__init__(title=title)

	async def on_submit(self, interaction: discord.Interaction):
		server = db.getServerById(interaction.guild.id)
		try:
			await self.bot.get_channel(1063941000696954930).send(embed=bot_functions.f_embed(
				f"Feedback from server *'{server.server_name}'* from user *'{interaction.user}'*",
				f"""
				**Title:** {self.feedback_title}\n
				**Category:** {self.category}\n
				**Description:\n** {self.description}
				""", 
				const.color_admin
				))	
		except Exception as e:
			await self.bot.get_channel(1063941000696954930).send(e)

		try:
			await interaction.response.send_message("")
		except:
			None
