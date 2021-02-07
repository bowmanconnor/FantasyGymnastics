from django.shortcuts import render, redirect, get_object_or_404
from .models import League
from .forms import NewLeagueForm
# Create your views here.

def create_league(request):
    if request.method == 'POST':
        form = NewLeagueForm(request.POST)
        if form.is_valid():
            league = form.save(commit=False)
            # league.manager = 1
            league.save()
            return redirect('home')
    else:
        form = NewLeagueForm()
    return render(request, 'core/create_league.html', {'form': form})

def home(request):
    context = {}
    context['leagues'] = League.objects.all()
    return render(request, 'core/home.html', context)