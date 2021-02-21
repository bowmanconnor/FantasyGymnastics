from django.contrib import admin
from .models import Gymnast, Score

# Register your models here.

class GymnastAdmin(admin.ModelAdmin):
    list_display = ('name', 'team')
    list_filter = ('team', 'year')
    search_fields = ('name', 'team')

class ScoreAdmin(admin.ModelAdmin):
    list_display = ('gymnast', 'meet', 'event', 'score', 'date')
    list_filter = ('meet', 'event')
    search_fields = ('gymnast__name', 'event')

admin.site.register(Gymnast, GymnastAdmin)
admin.site.register(Score, ScoreAdmin)