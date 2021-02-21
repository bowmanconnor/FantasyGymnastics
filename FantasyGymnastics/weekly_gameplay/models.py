from django.db import models
import core.models as core_models
# Create your models here.

class Matchup(models.Model):
    team1 = models.ForeignKey(core_models.FantasyTeam, related_name='Matchup', on_delete=models.CASCADE)
    team2 = models.ForeignKey(core_models.FantasyTeam, related_name='Matchup', on_delete=models.CASCADE)
    