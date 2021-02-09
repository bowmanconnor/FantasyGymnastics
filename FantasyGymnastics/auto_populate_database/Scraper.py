import requests
import json
from enum import Enum
import datetime
import random

# Define scraping URLs
BASE_URL = 'https://www.roadtonationals.com/'
RESULTS_URL = 'api/%s/results/%s/%s/%s/%s'
FINAL_RESULTS_URL = 'api/%s/finalresults/%s'
CURRENT_WEEK_URL = 'api/%s/currentweek/%s'
HA_DIFF_URL = 'api/%s/homeaway/%s'
ROSTER_URL = 'api/%s/rostermain/%s/%s/1'
GYMNAST_RESULTS_URL = 'api/%s/gymnast/%s/%s'

# List of common user agents for randomization
USER_AGENTS = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
			   'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
			   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
			   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
			   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
			   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15',
			   'Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1',
			   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Safari/605.1.15',
			   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15']

class ScraperConstants(Enum):
	'''Constants useful for making scraping calls'''
	Team = 0
	Individual = 1
	Men = 'men'
	Women = 'women'
	EarliestYear_Mens = 2012
	EarliestYear_Womens = 1998

class MensEvents(Enum):
	FloorExercise = 1
	PommelHorse = 2
	StillRings = 3
	Vault = 4
	ParallelBars = 5
	HighBar = 6
	AllAround = 7

class WomensEvents(Enum):
	Vault = 1
	UnevenBars = 2
	BalanceBeam = 3
	FloorExercise = 4
	AllAround = 5

class Scraper(object):
	'''Scraper of RoadToNationals website, all methods throw ScraperException'''

	def __init__(self):
		# Create HTTP session for making requests
		self.create_new_session()

	def create_new_session(self):
		self.session = requests.Session()

		random_user_agent_index = random.randint(0, len(USER_AGENTS)-1)
		self.session.headers = {'User-Agent': USER_AGENTS[random_user_agent_index]}

	def get_current_and_max_week(self, gender, year):
		'''
		Gets current season week and maximum week number given the current season year.
		@params
			gender: "men" or "women"
			year: season year
		@requires
			gender is either 'men' or 'women' and
			year is a valid season year for the gender
		@returns
			A JSON object with "week" and "max" keys that represent the current season week and max season week
		'''

		self.__check_gender(gender)		
		self.__check_year(gender, year)

		response = self.session.get(BASE_URL + (CURRENT_WEEK_URL % (gender.value, year)))
		return json.loads(response.text)

	def get_results(self, gender, year, week_number, team_or_individual, event):
		'''
		Gets team or individual results for certain gender, season, week, and event.
		@params
			gender: "men" or "women"
			year: season year
			week_number: week number of season
			team_or_individual: 0 for team results or 1 for individual results
			event: numerical value depending on gender chosen.
				if "men" specified for gender:
					1->FX, 2->PH, 3->SR, 4->VT, 5->PB, 6->HB, 7->AA
				if "women" specified for gender:
					1->VT, 2->UB, 3->BB, 4->FX, 5->AA
		@requires
			gender is either 'men' or 'women' and
			year is a valid season year for the gender and
			week_number is a valid week number of the season and
			team_or_individual is 0 or 1 and
			event is a valid event for the gender specified
		@returns
			A JSON object with the "data" and "schema" keys. "data" is a dictionary and "schema" is an object. "schema" contains various information about the available years to look through, 
			the current year, the number of weeks available to look through for each year, list of teams, and list of conferences.
			Each element of the "data" array represents the results and has the following keys:
				"rank", "name", "tid", "rqs", "usag", "reg", "con", "ave", and "high"
			The "schema" object has the following keys:
				"year", "years", "weeks", "cons", "teams", and "yearweeks"
		'''

		self.__check_gender(gender)
		self.__check_year(gender, year)

		if gender is ScraperConstants.Men:
			if event not in MensEvents:
				raise ScraperException('Invalid event specified for men.')
		elif gender is ScraperConstants.Women:
			if event not in WomensEvents:
				raise ScraperException('Invalid event specified for women.')

		if team_or_individual is not ScraperConstants.Team and team_or_individual is not ScraperConstants.Individual:
			raise ScraperException('Invalid option specified for team_or_individual.')

		response = self.session.get(BASE_URL + (RESULTS_URL % (gender.value, year, week_number, team_or_individual.value, event.value)))
		response_json = json.loads(response.text)

		if len(response_json['data']) == 0:
			raise ScraperException('Invalid week number specified.')

		return response_json

	def get_final_results(self, gender, year):
		'''
		Gets final results for the season.
		@params
			gender: "men" or "women"
			year: season year
		@requires
			gender is either 'men' or 'women' and
			year is a valid season year for the gender
		@returns
			A JSON object where only key is "data" array. Each element of the "data" array represents a team's final results and is an object containing the following keys:
				"rank", "team_name", "team_id", "ncaa_final", "ncaa", "nqa", "average_score", and "high_score"
		'''
		
		self.__check_gender(gender)
		self.__check_year(gender, year)

		response = self.session.get(BASE_URL + (FINAL_RESULTS_URL % (gender.value, year)))
		return json.loads(response.text)
	
	def get_home_away_diff(self, gender, year):
		'''
		Gets H/A diff for all teams, useful for obtaining list of all teams.
		@params
			gender: "men" or "women"
			year: season year
		@requires
			gender is either 'men' or 'women' and
			year is a valid season year for the gender
			@returns
				Returns JSON array where all teams are an object in the array with the following keys:
					"team_name", "team_id", "avgteam", "maxteam", "homeavg", "awayavg", "counthome", "countaway", and "diff"
		'''

		self.__check_gender(gender)
		self.__check_year(gender, year)

		response = self.session.get(BASE_URL + (HA_DIFF_URL % (gender.value, year)))
		return json.loads(response.text)

	def get_roster(self, gender, year, team_id):
		'''
		Gets roster for a team.
		@params
			gender: "men" or "women"
			year: season year
			team_id: numerical team id
		@requires
			gender is either 'men' or 'women' and
			year is a valid season year for the gender and
			team_id is the team id of a team that existed in the given year
		@returns
			JSON dictionary where each element is an object representing a person on the roster. Each object has the following keys:
				"id", "tid", "lname", "fname", "hometown", "fx", "ph", "sr", "v", "pb", "hb", "school_year", "events"
			where the keys representing events are either "1" or null depending on whether the person does them.
		'''

		self.__check_gender(gender)

		response = self.session.get(BASE_URL + (ROSTER_URL % (gender.value, year, team_id)))
		response_json = json.loads(response.text)

		if len(response_json) == 0:
			raise ScraperException('Either invalid year or team_id specified')

		return response_json

	def get_gymnast_meet_results(self, gender, year, gymnast_id):
		'''
		Gets all meet results for a gymnast.
		@params
			gender: "men" or "women"
			year: season year
			gymnast_id: RTN gymnast id
		@requires
			gender is either 'men' or 'women' and
			year is a valid season year for the gender and
			gymnast_id is the id of a gymnast who is of the specified gender and competed in the given year
		@returns
			JSON object with "team" and "meets" keys. "team" is a JSON object with information about the team of the gymnast and contains the following keys:
				"fname" == "0", "lname" == "1", "team_name" == "2"
			"meets" is an array where each element is a JSON object representing a meet that contains the following keys for both men and women:
				"fname", "lname", "all_around", "vault", "floor", "meet_date", "date", "home", "opponent", "meet_desc", "vt_url", "fx_url"
			the following keys for men:
				"phorse", "rings", "pbars", "highbar", "ph_url", "sr_url", "pb_url", "hb_url"
			and the following keys for women:
				"bars", "beam", "ub_url", "bb_url"
		'''
		self.__check_gender(gender)

		response = self.session.get(BASE_URL + (GYMNAST_RESULTS_URL % (gender.value, year, gymnast_id)))
		response_json = json.loads(response.text)

		if response_json['team'] == False:
			raise ScraperException('Either invalid year or gymnast_id specified')

		return response_json

	def __check_gender(self, gender):
		if gender is not ScraperConstants.Men and gender is not ScraperConstants.Women:
			raise ScraperException('Invalid gender specified.')

	def __check_year(self, gender, year):
		if int(year) > datetime.datetime.today().year:
			raise ScraperException('Invalid year specified.')

		if gender is ScraperConstants.Men:
			if int(year) < ScraperConstants.EarliestYear_Mens.value:
				raise ScraperException('Invalid year specified.')
		elif gender is ScraperConstants.Women:
			if int(year) < ScraperConstants.EarliestYear_Womens.value:
				raise ScraperException('Invalid year specified.')

class ScraperException(Exception):
	pass