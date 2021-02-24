from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from scraper.Scraper import Scraper, ScraperConstants
from core.models import Gymnast
import json, traceback, time
from weekly_gameplay.models import Average

GYMNAST_YEARS = {
    "1": "FR",
    "2": "SO",
    "3": "JR",
    "4": "SR"
}

class Command(BaseCommand):
    help = 'Imports gymnasts from RTN given a year'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int)

    def handle(self, *args, **options):
        scraper = Scraper()
        start_time = round(time.time() * 1000)

        print("Getting list of all teams for %s" % options['year'])
        # Try and get list of all teams
        try:
            teams = scraper.get_teams(ScraperConstants.Men, options['year'])
            print("Found %s teams" % len(teams))
        except:
            traceback.print_exc()
            return
        
        # For each team
        new_gymnasts = []
        num_skipped = 0
        for team in teams:
            # Get the roster for the team
            try:
                print("Getting roster for %s" % team['team_name'])
                roster = scraper.get_roster(ScraperConstants.Men, options['year'], team['id'])
            except:
                traceback.print_exc()
                return

            # For each gymnast on the roster, make a new Gymnast object and save it to the database
            for gymnast in roster:
                name = "%s %s" % (gymnast['fname'].strip(), gymnast['lname'].strip())
                g = Gymnast(name=name, rtn_id=gymnast['id'], team=team['team_name'], year=GYMNAST_YEARS[gymnast['school_year']])
                
                # Check if gymnast already exists in database to avoid readding
                if Gymnast.objects.filter(rtn_id=gymnast['id']).exists():
                    num_skipped = num_skipped + 1
                else:
                    new_gymnasts.append(g)
        
        # Save new gymnasts to database
        for gymnast in new_gymnasts:
            gymnast.save()
        
        print("")
        print("------ RESULTS ------")
        print("Added %s gymnasts" % len(new_gymnasts))
        print("Skipped %s existing gymnasts" % num_skipped)
        print("Took %s ms" % (round(time.time() * 1000) - start_time))