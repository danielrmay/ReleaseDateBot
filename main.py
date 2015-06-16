# -*- coding: utf-8 -*-

import praw
import datetime
import os
import pytz
import time
import codecs
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from dateutil import tz
from pytz import timezone
from rd_config import *

class Game:
	def __init__(self, names, hasReleaseDate, releaseDate, wikiLink):
		self.names = names
		self.hasReleaseDate = hasReleaseDate
		self.releaseDate = releaseDate
		self.wikiLink = wikiLink

	def containsName(self, name):
		hasMatched = False
		for storedName in self.names:
			if storedName.lower() == name.lower():
				hasMatched = True

		return hasMatched

def buildOutput(game, years, months, days, hours, minutes, seconds):
	output = "**[{0}]({1})** will be released in *".format(game.names[0], game.wikiLink)

	hasPrevious = False
	if(years != 0):
		hasPrevious = True
		output += "{0} years".format(years)

	if(months != 0):
		if(hasPrevious):
			output += ", "
		output += "{0} months".format(months)
		hasPrevious = True
	
	if(days != 0):
		if(hasPrevious):
			output += ", "
		output += "{0} days".format(days)
		hasPrevious = True
	
	if(hours != 0):
		if(hasPrevious):
			output += ", "
		output += "{0} hours".format(hours)
		hasPrevious = True
	
	if(minutes != 0):
		if(hasPrevious):
			output += ", "
		output += "{0} minutes".format(minutes)
		hasPrevious = True
	
	# always display seconds. This removes the complexity of having to add the "and" 
	# to the other values, which i'm not prioritising for this first version.
	if(hasPrevious):
		output += " and "
	output += "{0} seconds".format(seconds)
	
	output += ".*"

	return output

# important variables
replied_to_path = 'comments_replied_to.txt'
unknown_game_path = 'unknown_game.txt'
version = "0.1"
bot_footer = "\r\n\r\n---\r\n^ReleaseDateBot ^v" + version + " ^| [^PM ^feedback](http://www.reddit.com/message/compose/?to=ReleaseDateBot)"

match_prefix = '!ReleaseDate'
match_prefix_count = 12

games = []
games.append(Game(['Fallout 4', 'Fallout', 'Fallout4', 'Fall out', 'Fall out 4'], True, datetime(2015, 11, 10, 0, 0, 0), 'https://en.wikipedia.org/wiki/Fallout_4'))
games.append(Game(['Batman: Arkham Knight', 'Batman Arkham Knight', "Arkham Knight"], True, datetime(2015, 06, 23, 0, 0, 0), 'https://en.wikipedia.org/wiki/Batman:_Arkham_Knight'))
games.append(Game(['Final Fantasy XIV: Heavensward', 'Final Fantasy XIV', "Final Fantasy Heavensward", "Heavensward"], True, datetime(2015, 06, 23, 0, 0, 0), 'https://en.wikipedia.org/wiki/Final_Fantasy_XIV:_A_Realm_Reborn'))
games.append(Game(['The Division', "Tom Clancy's The Division", "Tom Clancy: The Division"], True, datetime(2016, 03, 8, 0, 0, 0), "https://en.wikipedia.org/wiki/Tom_Clancy%27s_The_Division"))
games.append(Game(['Need for Speed'], True, datetime(2015, 11, 03, 0, 0, 0), 'https://en.wikipedia.org/wiki/Need_for_Speed_(2015_video_game\)'))
games.append(Game(['Rise of the Tomb Raider', 'New Tomb Raider', 'Tomb Raider'], True, datetime(2015, 11, 10, 0, 0, 0), 'https://en.wikipedia.org/wiki/Rise_of_the_Tomb_Raider'))
games.append(Game(["Mirror's Edge Catalyst", "Mirror's Edge 2", "Mirrors Edge Catalyst", "Mirrors Edge 2"], True, datetime(2016, 02, 23, 0, 0, 0), 'https://en.wikipedia.org/wiki/Mirror%27s_Edge_Catalyst'))
games.append(Game(["F1 2015", "F1"], True, datetime(2015, 07, 21, 0, 0, 0), 'https://en.wikipedia.org/wiki/F1_2015_(video_game\)'))
games.append(Game(["MotoGP 2015", "F1"], True, datetime(2015, 06, 24, 0, 0, 0), 'https://en.wikipedia.org/wiki/MotoGP_15'))
games.append(Game(["Mad Max"], True, datetime(2015, 9, 04, 0, 0, 0), 'https://en.wikipedia.org/wiki/Mad_Max_(2015_video_game\)'))
games.append(Game(["FIFA 16", "FIFA 2016", "FIFA Soccer 16"], True, datetime(2015, 9, 15, 0, 0, 0), 'https://en.wikipedia.org/wiki/FIFA_16'))
games.append(Game(["Skylanders: Superchargers", "Skylanders Superchargers"], True, datetime(2015, 9, 20, 0, 0, 0), 'https://en.wikipedia.org/wiki/Skylanders:_SuperChargers'))
games.append(Game(["LEGO Dimensions"], True, datetime(2015, 9, 29, 0, 0, 0), 'https://en.wikipedia.org/wiki/Lego_Dimensions'))
games.append(Game(["Halo 5: Guardians", "Halo 5"], True, datetime(2015, 10, 27, 0, 0, 0), 'https://en.wikipedia.org/wiki/Halo_5:_Guardians'))
games.append(Game(["Call of Duty: Black Ops III", "Black Ops 3", "Call of Duty: Black Ops 3", "Call of Duty Black Ops III"], True, datetime(2015, 11, 06, 0, 0, 0), 'https://en.wikipedia.org/wiki/Call_of_Duty:_Black_Ops_III'))
games.append(Game(["Star Wars: Battlefront", "Star Wars Battlefront", "Battlefront"], True, datetime(2015, 11, 20, 0, 0, 0), 'https://en.wikipedia.org/wiki/Star_Wars_Battlefront_(2015_video_game\)'))
games.append(Game(["Rock Band 4"], True, datetime(2015, 10, 06, 0, 0, 0), 'https://en.wikipedia.org/wiki/Rock_Band_4'))
games.append(Game(["NHL 16", "NHL16"], True, datetime(2015, 9, 9, 0, 0, 0), 'https://en.wikipedia.org/wiki/NHL_(video_game_series\)'))
games.append(Game(["Tom Clancy's Rainbow Six Siege", "Rainbow Six Siege", "Tom Clancys Rainbow Six Siege"], True, datetime(2015, 10, 13, 0, 0, 0), 'https://en.wikipedia.org/wiki/Tom_Clancy''s_Rainbow_Six_Siege'))
games.append(Game(["Assassin's Creed Syndicate", "AC: Syndicate", "AC Syndicate"], True, datetime(2015, 10, 23, 0, 0, 0), 'https://en.wikipedia.org/wiki/Assassin\'s_Creed_Syndicate'))

# Release date unannounced:
games.append(Game(["Final Fantasy XV"], False, datetime(1970, 1, 1, 0, 0, 0), 'https://en.wikipedia.org/wiki/Final_Fantasy_XV'))
games.append(Game(["Street Fighter V", "Street Fighter"], False, datetime(1970, 1, 1, 0, 0, 0), 'https://en.wikipedia.org/wiki/Street_Fighter_V'))
games.append(Game(["Tony Hawk's Pro Skater 5", "Pro Skater 5", "THPS5"], False, datetime(1970, 1, 1, 0, 0, 0), 'https://en.wikipedia.org/wiki/Tony_Hawk%27s_Pro_Skater_5'))
games.append(Game(["Doom"], False, datetime(1970, 1, 1, 0, 0, 0), 'https://en.wikipedia.org/wiki/Doom_(2016_video_game\)'))
games.append(Game(["Dishonored 2"], False, datetime(1970, 1, 1, 0, 0, 0), 'https://en.wikipedia.org/wiki/Dishonored_2'))
games.append(Game(["Battleborn"], False, datetime(1970, 1, 1, 0, 0, 0), 'https://en.wikipedia.org/wiki/Battleborn_(video_game\)'))
games.append(Game(["Dead Island 2"], False, datetime(1970, 1, 1, 0, 0, 0), 'https://en.wikipedia.org/wiki/Dead_Island_2'))
games.append(Game(["Unravel"], False, datetime(1970, 1, 1, 0, 0, 0), 'https://en.wikipedia.org/wiki/Unravel_(video_game\)'))
games.append(Game(["Fable Legends"], False, datetime(1970, 1, 1, 0, 0, 0), 'https://en.wikipedia.org/wiki/Fable_Legends'))
games.append(Game(["Deux Ex: Mankind Divided", "Deus Ex Mankind Divided"], False, datetime(1970, 1, 1, 0, 0, 0), 'https://en.wikipedia.org/wiki/Deus_Ex:_Mankind_Divided'))
games.append(Game(["Dark Souls III", "Dark Souls 3"], False, datetime(1970, 1, 1, 0, 0, 0), 'https://en.wikipedia.org/wiki/Dark_Souls_III'))
games.append(Game(["Tom Clancy's Ghost Recon Wildlands", "Ghost Recon Wildlands", "Tom Clancys Ghost Recon Wildlands"], False,  datetime(1970, 1, 1, 0, 0, 0), 'https://en.wikipedia.org/wiki/Tom_Clancy%27s_Ghost_Recon_Wildlands'))
games.append(Game(["Plants vs. Zombies: Garden Warfare 2", "Garden Warfare 2", "Plants vs Zombies Garden Warfare 2", "Plants vs Zombies: Garden Warfare 2" ], False, datetime(1970, 1, 1, 0, 0, 0), 'https://en.wikipedia.org/wiki/Plants_vs._Zombies:_Garden_Warfare_2'))

hl3_names = ["Half-Life 3", "Half Life 3", "HL3"]
delta_tz = timezone('US/Pacific')

user_agent = ("ReleaseDate v" + version)
r = praw.Reddit(user_agent = user_agent)
r.login(REDDIT_USERNAME, REDDIT_PASSWORD)

if not os.path.isfile(unknown_game_path):
    open(unknown_game_path, 'a').close()

# Have we run this code before? If not, create an empty list
if not os.path.isfile(replied_to_path):
    comments_replied_to = []
    open(replied_to_path, 'a').close()

# If we have run the code before, load the list of posts we have replied to
else:
    # Read the file into a list and remove any empty values
    with open(replied_to_path, "r") as f:
        comments_replied_to = f.read()
        comments_replied_to = comments_replied_to.split("\n")
        comments_replied_to = filter(None, comments_replied_to)

while True:
	time.sleep(2)
	
	comments = praw.helpers.comment_stream(r, 'all', limit=None)
	
	for comment in comments:
		# Check to see if we have replied to this comment already
		if comment.id in comments_replied_to:
			break

		replied = False
		if comment.body.startswith(match_prefix):
			print("Found comment: " + comment.body)
			gamestring = comment.body[len(match_prefix):].strip()

			gameFound = False

			# HL3 easter egg
			for hl3_name in hl3_names:
				if gamestring.lower() == hl3_name.lower():
					print("Found a HL3 request. Replying...")
					gameFound = True
					comment_body = "Gah! Half-Life 3 will never be released if you keep talking about it!"
					comment_body += bot_footer
					comment.reply(comment_body)
					replied = True

			if not gameFound:
				# check if this game exists in our game array
				for game in games:
					if game.containsName(gamestring):
						print("Matched game '" + gamestring + "' to " + game.names[0])
						gameFound = True

						if game.hasReleaseDate:
							# convert 
							utc_datetime = datetime.utcnow()
							utc_datetime = utc_datetime.replace(tzinfo=pytz.utc)
							current_datetime = utc_datetime.astimezone(delta_tz)
							game_releasedate = game.releaseDate.replace(tzinfo=delta_tz)

							# figure out relative time delta between now until release date
							rd = relativedelta(current_datetime, game_releasedate)

							if rd.years >= 0 and rd.months >= 0 and rd.days >= 0 and rd.hours >= 0 and rd.minutes >= 0 and rd.seconds >= 0:
								output = "**[{0}]({1})** has been released!".format(game.names[0], game.wikiLink)
							else:
								years = abs(rd.years)
								months = abs(rd.months)
								days = abs(rd.days)
								hours = abs(rd.hours)
								minutes = abs(rd.minutes)
								seconds = abs(rd.seconds)

								output = buildOutput(game, years, months, days, hours, minutes, seconds)
							
							output += bot_footer
							print("Posting reply:\r\n\r\n {0}").format(output)
							comment.reply(output)
							replied = True
						else:
							comment_body = "Sorry, **[{0}]({1})** has been announced but no specific release date has been published yet.\r\n\r\nIf this message is incorrect please let me know via PM!".format(game.names[0], game.wikiLink)
							comment_body += bot_footer
							comment.reply(comment_body)

							replied = True

				if not gameFound:
					comment_body = "Sorry, I'm not able to recognize that game's release date yet. ¯\\\_(ツ)_/¯ \r\n\r\nI have logged this interaction and my author will add it soon!"
					comment_body += bot_footer
					comment.reply(comment_body)

					with open(unknown_game_path, "a") as f:
						f.write(gamestring + " ~ " + comment.id + "\n")   

					replied = True

		if replied:
			comments_replied_to.append(comment.id)
			with open(replied_to_path, "a") as f:
				f.write(comment.id + "\n")     

