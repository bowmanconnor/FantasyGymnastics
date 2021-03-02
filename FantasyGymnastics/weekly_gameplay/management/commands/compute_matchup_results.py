from django.core.management.base import BaseCommand
import decimal 
from core.models import Score, League, LineUp
from weekly_gameplay.models import Matchup
import time
EVENT_NAMES_DICT = {
    "floor": "FX",
    "phorse": "PH",
    "rings": "SR",
    "vault": "VT",
    "pbars": "PB",
    "highbar": "HB"
}

def team_score(lineups):
        total = 0
        for lineup in lineups:
            scores = []
            for gymnast in lineup.gymnasts.all():
                gymnast_scores = Score.objects.filter(gymnast=gymnast, event=lineup.event, week=lineup.week)
                if gymnast_scores.exists():
                    gymnasts_highest = gymnast_scores.first()
                    for score in gymnast_scores:
                        if score.score > gymnasts_highest.score:
                            gymnasts_highest = score
                    scores.append(gymnasts_highest.score)
            if len(scores) > int(lineup.team.league.event_count_size):
                scores.sort(reverse=True)
                scores = scores[:int(lineup.team.league.event_count_size)]
            for score in scores:
                total += score
        return total

class Command(BaseCommand):
    help = 'Computes matchups for a week and creates next weeks lineups'

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
            matchups = Matchup.objects.filter(week=options['week'], league=league)
            for matchup in matchups:
                team1 = matchup.team1
                team2 = matchup.team2
                team1_lineups = LineUp.objects.filter(team=matchup.team1, week=options['week'])
                team2_lineups = LineUp.objects.filter(team=matchup.team2, week=options['week'])
                team1_score = team_score(team1_lineups)
                team2_score = team_score(team2_lineups)
                if team1_score > team2_score:
                    team1.wins += 1
                    team2.losses += 1
                elif team2_score > team1_score:
                    team2.wins += 1
                    team1.losses += 1
                team1.save()
                team2.save()

                for event in EVENT_NAMES_DICT:
                    if not LineUp.objects.filter(team=team1, event=EVENT_NAMES_DICT[event], week=options['week']+1).exists():
                        LineUp.objects.create(team=team1, event=EVENT_NAMES_DICT[event], week=options['week']+1)
                        new_lineups += 1
                    else:    
                        skipped_new_lineups += 1
                    if not LineUp.objects.filter(team=team2, event=EVENT_NAMES_DICT[event], week=options['week']+1).exists():
                        LineUp.objects.create(team=team2, event=EVENT_NAMES_DICT[event], week=options['week']+1)
                        new_lineups += 1
                    else:
                        skipped_new_lineups += 1

                count += 1

        print("")
        print("------ RESULTS ------")
        print("Computed %s matchups" % count)
        print("Created %s new lineups" % new_lineups)
        print("Skipped %s existing lineups" % skipped_new_lineups)
        print("Took %s ms" % (round(time.time() * 1000) - start_time))


