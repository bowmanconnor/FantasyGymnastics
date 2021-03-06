from django.db import models
from django.contrib.auth.models import User
import random

class Gymnast(models.Model):
    YEAR_CHOICES = [('FR' , 'Freshman'), ('SO' , 'Sophomore'), ('JR' , 'Junior'), ('SR' , 'Senior')]
    rtn_id = models.CharField(max_length=10, blank=False)
    name = models.CharField(max_length=50, blank=False)
    team = models.CharField(max_length=100, blank=False)
    year = models.CharField(max_length=2, choices=YEAR_CHOICES, blank=False)

    class Meta:
        unique_together = ('name', 'team')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class League(models.Model):
    manager = models.ForeignKey(User, related_name='League', on_delete=models.CASCADE, null=True, blank=True) #how do these look, cutie?
    name = models.CharField(max_length=50, blank=False)
    roster_size = models.PositiveIntegerField(blank=False)
    lineup_size = models.PositiveIntegerField(blank=False)
    event_lineup_size = models.PositiveIntegerField(blank=False)
    event_count_size = models.PositiveIntegerField(blank=False)
    requested_to_join = models.ManyToManyField(User, related_name="RequestedLeague", blank=True)
    drafted = models.ManyToManyField(Gymnast, related_name="DraftedGymnasts", blank=True)
    currently_drafting = models.PositiveIntegerField(default=0, blank=True)

    def __str__(self):
        return self.name
    
    # Create an ordering from 0 through num teams - 1 and distribute to each team
    def generate_drafting_order(self):
        teams = FantasyTeam.objects.filter(league=self)
        num_teams = len(teams)
        ordering = random.sample(range(num_teams), num_teams)
        i = 0
        for team in teams:
            team.draft_position = ordering[i]
            team.save()
            i = i + 1


class FantasyTeam(models.Model):
    user = models.ForeignKey(User, related_name='FantasyTeam', on_delete=models.CASCADE)
    league = models.ForeignKey(League, related_name='FantasyTeam', on_delete=models.CASCADE)
    roster = models.ManyToManyField(Gymnast, related_name='FantasyTeam', blank=True)
    name = models.CharField(max_length=50, blank=False)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    draft_position = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'league')

    def __str__(self):
        return str(self.name)

class LineUp(models.Model):
    EVENT_CHOICES = [('FX' , 'Floor Exercise'), ('PH' , 'Pommel Horse'), ('SR' , 'Still Rings'), ('VT' , 'Vault'), ('PB' , 'Parallel Bars'), ('HB' , 'Horizontal Bar')]
    team = models.ForeignKey(FantasyTeam, related_name='LineUp', on_delete = models.CASCADE, blank=False)
    event = models.CharField(max_length=2, choices = EVENT_CHOICES, blank=False)
    gymnasts = models.ManyToManyField(Gymnast, related_name = 'LineUp', blank=True)
    week = models.PositiveIntegerField(blank=False)
    class Meta:
        unique_together = ('team', 'event', 'week')
        ordering = ['id']

    def __str__(self):
        return str(self.team) + "'s " + str(self.event) + " week: " + str(self.week)

class Score(models.Model):
    EVENT_CHOICES = [('FX' , 'Floor Exercise'), ('PH' , 'Pommel Horse'), ('SR' , 'Still Rings'), ('VT' , 'Vault'), ('PB' , 'Parallel Bars'), ('HB' , 'Horizontal Bar')]
    gymnast = models.ForeignKey(Gymnast, related_name='Scores', on_delete=models.CASCADE, null=False, blank=False)
    date = models.DateField()
    week = models.PositiveIntegerField(blank=False)
    meet = models.CharField(max_length=100)
    event = models.CharField(max_length=2, choices = EVENT_CHOICES, blank=False)
    score = models.DecimalField(max_digits=6, decimal_places=4)

    class Meta:
        unique_together = ('gymnast', 'date', 'event')

    def __str__(self):
        return str(round(self.score,2))