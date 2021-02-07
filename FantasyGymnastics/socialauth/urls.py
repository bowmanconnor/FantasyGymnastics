from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from socialauth import views as social_auth_views
from core import views as core_views

urlpatterns = [
    path('', include("django.contrib.auth.urls")),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('login', social_auth_views.login, name="login"),
    path('logout', auth_views.LogoutView.as_view(), name="logout")
]
