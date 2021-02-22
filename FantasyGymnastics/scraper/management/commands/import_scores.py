from django.core.management.base import BaseCommand, CommandError
from scraper.Scraper import Scraper, ScraperConstants
from core.models import Gymnast, Score
import json, traceback, time

EVENT_NAMES_DICT = {
    "floor": "FX",
    "phorse": "PH",
    "rings": "SR",
    "vault": "VT",
    "pbars": "PB",
    "highbar": "HB"
}

class Command(BaseCommand):
    help = 'Retrieves scores from a week'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int)
        parser.add_argument('week', type=int)

    def handle(self, *args, **options):
        scraper = Scraper()
        start_time = round(time.time() * 1000)

        print("Getting all matchups for week %s" % options['week'])
        try:
            # Get all weeks and their dates for the season
            weeks = scraper.get_year_weeks(ScraperConstants.Men, options['year'])
            # Get date to scrape specified week
            date = [week for week in weeks if int(week['wk']) == options['week']][0]['date']
        except:
            traceback.print_exc()
            return
        
        try:
            # Get schedule for the week
            schedule = scraper.get_schedule(ScraperConstants.Men, date)
        except:
            traceback.print_exc()
            return
        
        # Create a list of (meet id, day of meet, meet name)
        meets = []
        # For each day in the schedule with a meet on it
        for day in schedule:
            # For each meet on that day
            for meet in schedule[day]['meets']:
                # Create a name for the meet depenending on home vs. away teams or virtua;
                away_teams = meet['away_teams']
                home_teams = meet['home_teams']
                if home_teams == None:
                    meet_name = "%s (Virtual)" % away_teams
                else:
                    meet_name = "%s @ %s" % (away_teams, home_teams)
                
                # Add to list of (meet id, day of meet, meet name)
                meets.append((meet['meet_id'], day, meet_name))

        # Keep track of new scores added and number skipped
        scores = []
        num_skipped = 0
        # Go through list of (meet id, day of meet, meet name)
        for meet_id, day, meet_name in meets:
            print("Getting meet results for %s" % meet_name)
            # Get the meet's results
            try:
                meet_results = scraper.get_meet_results(ScraperConstants.Men, meet_id)
            except:
                traceback.print_exc()
                return

            # Get the scores of every person who competed in the meet and save them
            # For each event in the meet's results
            for event_index_name in EVENT_NAMES_DICT:
                # Get each score for the event
                for score in meet_results[event_index_name]:
                    # Lookup the gymnast who had the score
                    gymnast = Gymnast.objects.filter(rtn_id=score['gid']).first()
                    # Create a new score object
                    score = Score(event=EVENT_NAMES_DICT[event_index_name], score=float(score['score']), gymnast=gymnast, date=day, meet=meet_name)
                    
                    # Check if the score already exists in the database
                    if Score.objects.filter(gymnast=gymnast, date=day, event=EVENT_NAMES_DICT[event_index_name]).exists():
                        num_skipped = num_skipped + 1
                    else:
                        scores.append(score)

        # Save new scores to the database
        for score in scores:
            score.save()

        print("")
        print("------ RESULTS ------")
        print("Added %s scores" % len(scores))
        print("Skipped %s existing scores" % num_skipped)
        print("Took %s ms" % (round(time.time() * 1000) - start_time))