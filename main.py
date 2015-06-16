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

class Game:
	def __init__(self, names, releaseDate, wikiLink):
		self.names = names
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
games.append(Game(['Fallout 4', 'Fallout', 'Fallout4', 'Fall out', 'Fall out 4'], datetime(2015, 11, 10, 0, 0, 0), 'https://en.wikipedia.org/wiki/Fallout_4'))
games.append(Game(['Batman: Arkham Knight', 'Batman Arkham Knight', "Arkham Knight"], datetime(2015, 06, 23, 0, 0, 0), 'https://en.wikipedia.org/wiki/Batman:_Arkham_Knight'))
games.append(Game(['Final Fantasy XIV: Heavensward', 'Final Fantasy XIV', "Final Fantasy Heavensward", "Heavensward"], datetime(2015, 06, 23, 0, 0, 0), 'https://en.wikipedia.org/wiki/Final_Fantasy_XIV:_A_Realm_Reborn'))

delta_tz = timezone('US/Pacific')

user_agent = ("ReleaseDate v" + version)
r = praw.Reddit(user_agent = user_agent)
r.login('','')

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
	# Gaming subreddit comments:
	#multi_reddits = r.get_subreddit('test+fallout+gaming+games')
	multi_reddits = r.get_subreddit('test+fallout')
	comments = multi_reddits.get_comments()

	#print("Retrieved comments: " + str(len(list(comments))))
	# Test submission:
	# submission = r.get_submission(submission_id='39yq1s')
	# comments = praw.helpers.flatten_tree(submission.comments)

	for comment in comments:
		# Check to see if we have replied to this comment already
		if comment.id in comments_replied_to:
			break

		replied = False
		if comment.body.startswith(match_prefix):
			print("Found comment: " + comment.body)
			gamestring = comment.body[len(match_prefix):].strip()

			gameFound = False
			# check if this game exists in our game array
			for game in games:
				if game.containsName(gamestring):
					print("Matched game '" + gamestring + "' to " + game.names[0])
					gameFound = True
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
					print(output)
					print("Posting reply.")
					comment.reply(output)
					replied = True

			if not gameFound:
				comment_body = "Sorry, I'm not able to recognize that game's release date yet. ¯\\\_(ツ)_/¯ \r\n\r\nI have logged this interaction and my author will add it soon!"
				comment_body += bot_footer
				comment.reply(comment_body)

				with open(unknown_game_path, "a") as f:
					f.write(gamestring + "\n")   

				replied = True


		if replied:
			comments_replied_to.append(comment.id)
			with open(replied_to_path, "a") as f:
				f.write(comment.id + "\n")     

