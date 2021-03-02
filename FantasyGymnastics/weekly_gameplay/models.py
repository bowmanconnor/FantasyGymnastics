from django.db import models
import core.models as core_models
# Create your models here.

class Matchup(models.Model):
    team1 = models.ForeignKey(core_models.FantasyTeam, related_name='Matchup1', on_delete=models.CASCADE)
    team2 = models.ForeignKey(core_models.FantasyTeam, related_name='Matchup2', on_delete=models.CASCADE)
    league = models.ForeignKey(core_models.League, related_name='Matchup', on_delete=models.CASCADE)
    week = models.PositiveIntegerField(blank=False)

    def __str__(self):
        return str(self.team1) + " " + str(self.team2) + " " + str(self.week)

    class Meta:
        unique_together = ('team1', 'team2', 'week')
        

class Average(models.Model):
    EVENT_CHOICES = [('FX' , 'Floor Exercise'), ('PH' , 'Pommel Horse'), ('SR' , 'Still Rings'), ('VT' , 'Vault'), ('PB' , 'Parallel Bars'), ('HB' , 'Horizontal Bar')]
    gymnast = models.ForeignKey(core_models.Gymnast, related_name="Average", on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=6, decimal_places=4)
    event = models.CharField(max_length=2, choices = EVENT_CHOICES, blank=False)
    number_of_scores = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return str(round(self.score,2))