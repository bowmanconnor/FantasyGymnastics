from django.shortcuts import render, redirect, get_object_or_404
from .models import League, FantasyTeam
from .forms import NewLeagueForm
from django.views.generic import UpdateView, DetailView
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

class view_league_detail(DetailView):
    model = League
    template_name = 'core/view_league.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'league'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teams'] = FantasyTeam.objects.filter(league_id=context['object'].id)
        return context
        

def home(request):
    context = {}
    context['leagues'] = League.objects.all()
    return render(request, 'core/home.html', context)