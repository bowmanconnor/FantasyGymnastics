from django.contrib import admin
from django.urls import path

from core import views as views

urlpatterns = [
    path('create_league/', views.create_league, name="create_league"),
    path('', views.home, name="home"),
]
