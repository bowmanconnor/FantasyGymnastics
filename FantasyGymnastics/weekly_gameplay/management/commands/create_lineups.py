from django.core.management.base import BaseCommand
import decimal 
from core.models import League, LineUp, FantasyTeam
import time
EVENT_NAMES_DICT = {
    "floor": "FX",
    "phorse": "PH",
    "rings": "SR",
    "vault": "VT",
    "pbars": "PB",
    "highbar": "HB"
}


class Command(BaseCommand):
    help = 'Creates new lineups for teams who did not have matchups in past week'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int)
        parser.add_argument('week', type=int)


    def handle(self, *args, **options):
        print("Computing matchups results for week %s" % options['week'])
        start_time = round(time.time() * 1000)
        count = 0
        new_lineups = 0
        skipped_new_lineups = 0
        leagues = League.objects.all()
        for league in leagues:
            teams = FantasyTeam.objects.filter(league=league)
            for team in teams:
                for event in EVENT_NAMES_DICT:
                    if not LineUp.objects.filter(team=team, event=EVENT_NAMES_DICT[event], week=options['week']).exists():
                        LineUp.objects.create(team=team, event=EVENT_NAMES_DICT[event], week=options['week'])
                        new_lineups += 1
                    else:    
                        skipped_new_lineups += 1
                count += 1

        print("")
        print("------ RESULTS ------")
        print("Created %s new lineups" % new_lineups)
        print("Skipped %s existing lineups" % skipped_new_lineups)
        print("Took %s ms" % (round(time.time() * 1000) - start_time))


