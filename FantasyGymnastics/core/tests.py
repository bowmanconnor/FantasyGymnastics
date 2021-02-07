from django.urls import reverse
from django.urls import resolve
from django.test import TestCase
from .views import home, create_league

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


class CreateLeagueTests(TestCase):
    def setUp(self):
        url = reverse('create_league')
        self.response = self.client.get(url)

    def test_create_league_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_create_league_url_resolves_create_league_view(self):
        view = resolve('/create_league/')
        self.assertEquals(view.func, create_league)