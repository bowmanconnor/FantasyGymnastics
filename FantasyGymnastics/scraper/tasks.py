from celery import shared_task
from django.core.management import call_command
from .Scraper import Scraper, ScraperConstants
import datetime

# Task to call import_gymnasts command
@shared_task
def import_gymnasts():
    call_command("import_gymnasts", str(datetime.date.today().year))

# Task to call import_scores command
@shared_task
def import_scores():
    # Get the current week of the season
    scraper = Scraper()
    year = datetime.date.today().year
    current_week = scraper.get_current_and_max_week(ScraperConstants.Men, year)['week']

    call_command("import_scores", str(year), current_week)