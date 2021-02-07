from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class League(models.Model):
    manager = models.ForeignKey(User, related_name='League', on_delete=models.CASCADE, null=True, blank=True) #how do these look, cutie?
    name = models.CharField(max_length=50, blank=False)
    roster_size = models.PositiveIntegerField(blank=False)
    lineup_size = models.PositiveIntegerField(blank=False)
    event_lineup_size = models.PositiveIntegerField(blank=False)
    event_count_size = models.PositiveIntegerField(blank=False)
    
class Gymnast(models.Model):
    YEAR_CHOICES = [('FR' , 'Freshman'), ('SO' , 'Sophomore'), ('JR' , 'Junior'), ('SR' , 'Senior')]
    name = models.CharField(max_length=50, blank=False)
    team = models.CharField(max_length=100, blank=False)
    year = models.CharField(max_length=2, choices=YEAR_CHOICES, blank=False)

class FantasyTeam(models.Model):
    user = models.ForeignKey(User, related_name='FantasyTeam', on_delete=models.CASCADE)
    league = models.ForeignKey(League, related_name='FantasyTeam', on_delete=models.CASCADE)
    gymnasts = models.ManyToManyField(Gymnast, related_name='FantasyTeam', blank=True)
    name = models.CharField(max_length=50, blank=False)

    class Meta:
        unique_together = ('user', 'league')

class Scores(models.Model):
    gymnast = models.ForeignKey(Gymnast, related_name='Scores', on_delete=models.CASCADE, null=False, blank=False)
    date = models.DateField()
    meet = models.CharField(max_length=100)

    floor = models.DecimalField(max_digits=4, decimal_places=2)
    pommel_horse = models.DecimalField(max_digits=4, decimal_places=2)
    rings = models.DecimalField(max_digits=4, decimal_places=2)
    vault = models.DecimalField(max_digits=4, decimal_places=2)
    parallel_bars = models.DecimalField(max_digits=4, decimal_places=2)
    high_bar = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        unique_together = ('gymnast', 'date', 'meet')
 
