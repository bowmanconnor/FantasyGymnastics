from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from core.models import FantasyTeam

@login_required
def index(request, league_pk):
    if FantasyTeam.objects.filter(user=request.user, league=league_pk).exists():
        return render(request, 'draft/draft_test.html', {'league_pk': league_pk})
    else:
        return redirect('home')