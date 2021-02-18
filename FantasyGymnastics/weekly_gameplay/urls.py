from django.contrib import admin
from django.urls import path
from core import views as core_views
import weekly_gameplay.views as weekly_views

urlpatterns = [
    path('team/<int:team_pk>/add_gymnast_to_roster/<int:gymnast_pk>/', weekly_views.add_gymnast_to_roster, name = 'add_gymnast_to_roster'),
    path('team/<int:team_pk>/remove_gymnast_to_roster/<int:gymnast_pk>/', weekly_views.remove_gymnast_from_roster, name = 'remove_gymnast_to_roster'),
]
