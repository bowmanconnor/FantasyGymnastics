from django.urls import reverse
from django.urls import resolve
from django.contrib.auth.models import User
from django.test.client import Client
from django.test import TestCase
from .views import *
from .models import FantasyTeam, League

# Tests that the urls are returning a status code of 200 and the urls are showing their appropriate views
class HomeTests(TestCase):
    def setUp(self):
        url = reverse('home')
        self.response = self.client.get(url)
    
    def test_home_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        view = resolve('/')
        self.assertEquals(view.func, home)

class LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('grippy', 'grippy@MyFGL.com', 'G3tAGr1p!')

    def test_login_status_code(self):
        self.client.login(username='grippy', password='G3tAGr1p!')
        view = resolve('/authentication/login/')
        response = self.client.get(reverse(view.func))
        self.assertEqual(response.status_code, 200)


class LeagueTests(TestCase):
    def setUp(self):
        url = reverse('create_league')
        self.user = User.objects.create_user('grippy', 'grippy@MyFGL.com', 'G3tAGr1p!')
        self.client.login(username='grippy', password='G3tAGr1p!')
        self.response = self.client.get(url)
        self.league = League.objects.create(
            manager = self.user,
            name = self.user.username,
            roster_size = 17,
            lineup_size = 15,
            event_lineup_size = 4,
            event_count_size = 3
        )

    def test_create_league_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_create_league_url_resolves_create_league_view(self):
        view = resolve('/league/create/')
        self.assertEquals(view.func, create_league)

    def test_view_league_view_status_code(self):
        url = reverse('view_league', kwargs={'pk': 1})
        self.response = self.client.get(url)
        self.assertEquals(self.response.status_code, 200)

    def test_view_league_view_failure_status_code(self):
        url = reverse('view_league', kwargs={'pk': 9999})
        self.response = self.client.get(url)
        self.assertEquals(self.response.status_code, 404)

    def test_view_league_url_resolves_view_league_view(self):
        view = resolve('/league/view/1/')
        self.assertEquals(view.func.__name__, LeagueDetailView.as_view().__name__)

    def test_edit_league_view_status_code(self):
        url = reverse('edit_league', kwargs={'pk': 1})
        self.response = self.client.get(url)
        self.assertEquals(self.response.status_code, 200)
    
    def test_edit_league_view_failure_status_code(self):
        url = reverse('edit_league', kwargs={'pk': 9999})
        self.response = self.client.get(url)
        self.assertEquals(self.response.status_code, 404)

    def test_edit_league_url_resolves_edit_league_view(self):
        view = resolve('/league/edit/1/')
        self.assertEquals(view.func.__name__, LeagueUpdateView.as_view().__name__)


class LeagueSearchTests(TestCase):
    def setUp(self):
        url = "%s?query=%s" % (reverse('league_search_results'), "")
        self.response = self.client.get(url)
    
    def test_league_search_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)
    
    def test_league_search_url_resolves_league_search_view(self):
        view = resolve('/league/search/')
        self.assertEquals(view.func.__name__, LeagueSearchResultsView.as_view().__name__)


class TeamTests(TestCase):
    def setUp(self):
        url = reverse('create_team', kwargs={'pk': 1})
        self.user = User.objects.create_user('grippy', 'grippy@MyFGL.com', 'G3tAGr1p!')
        self.client.login(username='grippy', password='G3tAGr1p!')
        self.response = self.client.get(url)
        self.league = League.objects.create(
            manager = self.user,
            name = self.user.username,
            roster_size = 17,
            lineup_size = 15,
            event_lineup_size = 4,
            event_count_size = 3
        )
        self.team = FantasyTeam.objects.create(
            user = self.user,
            league = self.league,
            name = 'All Grip No Gripe'
        )

    def test_create_team_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_create_team_url_resolves_create_team_view(self):
        view = resolve('/league/1/team/create/')
        self.assertEquals(view.func, create_team)

    def test_view_team_view_status_code(self):
        url = reverse('view_team', kwargs={'pk': 1})
        self.response = self.client.get(url)
        self.assertEquals(self.response.status_code, 200)

    def test_view_team_view_failure_status_code(self):
        url = reverse('view_team', kwargs={'pk': 9999})
        self.response = self.client.get(url)
        self.assertEquals(self.response.status_code, 404)

    def test_view_team_url_resolves_view_team_view(self):
        view = resolve('/team/view/1/')
        self.assertEquals(view.func.__name__, FantasyTeamDetailView.as_view().__name__)

    def test_edit_team_view_status_code(self):
        url = reverse('edit_team', kwargs={'pk': 1})
        self.response = self.client.get(url)
        self.assertEquals(self.response.status_code, 200)
    
    def test_edit_team_view_failure_status_code(self):
        url = reverse('edit_team', kwargs={'pk': 9999})
        self.response = self.client.get(url)
        self.assertEquals(self.response.status_code, 404)

    def test_edit_team_url_resolves_edit_team_view(self):
        view = resolve('/team/edit/1/')
        self.assertEquals(view.func.__name__, FantasyTeamUpdateView.as_view().__name__)

# import datetime

# tests = {}

# # Meet in future; Meet time 0; Now before noon
# meet_datetime = datetime.datetime(2021, 3, 28, 0, 0, 0)
# now = datetime.datetime(2021, 3, 27, 11, 0, 0)
# tests['Meet in future; Meet time 0; Now before noon'] = [meet_datetime, now]

# # Meet in future; Meet time 0; Now after noon
# meet_datetime = datetime.datetime(2021, 3, 28, 0, 0, 0)
# now = datetime.datetime(2021, 3, 27, 13, 0, 0)
# tests['Meet in future; Meet time 0; Now after noon'] = [meet_datetime, now]

# # Meet today ; Meet time 0; Now before noon
# meet_datetime = datetime.datetime(2021, 3, 28, 0, 0, 0)
# now = datetime.datetime(2021, 3, 28, 11, 0, 0)
# tests['Meet today ; Meet time 0; Now before noon'] = [meet_datetime, now]

# # Meet today ; Meet time 0; Now past noon
# meet_datetime = datetime.datetime(2021, 3, 28, 0, 0, 0)
# now = datetime.datetime(2021, 3, 28, 13, 0, 0)
# tests['Meet today ; Meet time 0; Now past noon'] = [meet_datetime, now]

# # Meet in past ; Meet time 0; Now before noon
# meet_datetime = datetime.datetime(2021, 3, 28, 0, 0, 0)
# now = datetime.datetime(2021, 3, 29, 11, 0, 0)
# tests['Meet in past ; Meet time 0; Now before noon'] = [meet_datetime, now]

# # Meet in past ; Meet time 0; Now past noon
# meet_datetime = datetime.datetime(2021, 3, 28, 0, 0, 0)
# now = datetime.datetime(2021, 3, 29, 13, 0, 0)
# tests['Meet in past ; Meet time 0; Now past noon'] = [meet_datetime, now]




# # Meet in future; Meet time non 0; Now before start
# meet_datetime = datetime.datetime(2021, 3, 28, 17, 0, 0)
# now = datetime.datetime(2021, 3, 27, 16, 0, 0)
# tests['Meet in future; Meet time non 0; Now before start'] = [meet_datetime, now]

# # Meet in future; Meet time non 0; Now after start
# meet_datetime = datetime.datetime(2021, 3, 28, 17, 0, 0)
# now = datetime.datetime(2021, 3, 27, 18, 0, 0)
# tests['Meet in future; Meet time non 0; Now after start'] = [meet_datetime, now]

# # Meet today ; Meet time non 0; Now before start
# meet_datetime = datetime.datetime(2021, 3, 28, 17, 0, 0)
# now = datetime.datetime(2021, 3, 28, 12, 0, 0)
# tests['Meet today ; Meet time non 0; Now before start'] = [meet_datetime, now]

# # Meet today ; Meet time non 0; Now past start
# meet_datetime = datetime.datetime(2021, 3, 28, 17, 0, 0)
# now = datetime.datetime(2021, 3, 28, 21, 0, 0)
# tests['Meet today ; Meet time non 0; Now past start'] = [meet_datetime, now]

# # Meet in past ; Meet time non 0; Now before start
# meet_datetime = datetime.datetime(2021, 3, 28, 17, 0, 0)
# now = datetime.datetime(2021, 3, 29, 16, 0, 0)
# tests['Meet in past ; Meet time non 0; Now before start'] = [meet_datetime, now]

# # Meet in past ; Meet time non 0; Now past start
# meet_datetime = datetime.datetime(2021, 3, 28, 17, 0, 0)
# now = datetime.datetime(2021, 3, 29, 17, 0, 0)
# tests['Meet in past ; Meet time non 0; Now past start'] = [meet_datetime, now]


# for test, value in tests.items():
#     print(test)
#     meet_started = value[0]
#     now = value[1]
#     print("Meet start: %s" % meet_started)
#     print("now: %s" % now)
#     print("Should the gymnast be locked?")

#     if now.date() > meet_started.date():
#         print(True)
#     elif now.date() == meet_started.date():
#         if meet_started.time() != datetime.time(0, 0, 0):
#             if now.time() > meet_started.time():
#                 print(True)
#             else: 
#                 print(False)
#         else:
#             if now.time() >= datetime.time(12, 0, 0):
#                 print(True)
#             else: 
#                 print(False)
#     else:
#         print(False)
#     print("---------------------")