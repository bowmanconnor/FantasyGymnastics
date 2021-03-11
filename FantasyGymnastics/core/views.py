from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import League, FantasyTeam, Gymnast, LineUp, Score
from django.views.generic import UpdateView, DetailView, DeleteView, ListView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from scraper.Scraper import ScraperConstants
from scraper.Scraper import Scraper
from datetime import datetime
from weekly_gameplay.models import Average, Matchup
from django.db.models import Q
from .forms import NewLeagueForm, NewFantasyTeamForm, NewGymnastForm

#Helper Function
def create_team_with_lineups(user, league):
    scraper = Scraper()

    team = FantasyTeam.objects.create(
        user=user,
        league=league,
        name=str(user.username)+"'s Team")
    events = ['FX', 'PH', 'SR', 'VT', 'PB', 'HB']
    for i in range(6):
        lineup = LineUp.objects.create(
            team=team,
            event=events[i],
            week=int(scraper.get_current_and_max_week(ScraperConstants.Men, datetime.now().year)['week'])
        )
        lineup.save()
        
@login_required
def create_league(request):
    if request.method == 'POST':
        form = NewLeagueForm(request.POST)
        if form.is_valid():
            league = form.save(commit=False)
            league.manager = request.user
            print(league)
            league.save()
            create_team_with_lineups(request.user, league)
            return redirect('league_standings', pk=league.pk)
    else:
        form = NewLeagueForm()
    return render(request, 'core/create_league.html', {'form': form})

@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'core/user_list.html', {'users': users})

# is now league standings
class LeagueStandings(DetailView):
    model = League
    template_name = 'core/league_standings.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'league'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teams'] = FantasyTeam.objects.filter(league_id=context['object'].id).order_by('-wins', 'name')
        scraper = Scraper()
        context['current_week'] = int(scraper.get_current_and_max_week(ScraperConstants.Men, datetime.now().year)['week'])
        context['max_week'] = int(scraper.get_current_and_max_week(ScraperConstants.Men, datetime.now().year)['max'])
        context['matchups'] = Matchup.objects.filter(team1__in=context['teams'])
        return context

class UpdateLeague(UserPassesTestMixin, UpdateView):
    model = League
    form_class = NewLeagueForm

    template_name = 'core/edit_league.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'league'

    def test_func(self):
        self.object = self.get_object()
        return self.request.user == self.object.manager

    def form_valid(self, form):
        league = form.save(commit=False)
        league.save()
        return redirect('league_standings', pk=league.pk)

class SearchLeagues(ListView):
    model = League
    template_name = 'core/league_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        query = self.request.GET.get('query')
        if query:
            context['leagues'] = League.objects.filter(name__icontains=query)
        else:
            context['leagues'] = League.objects.all()
        return context
 
        
@login_required
def request_to_join_league(request, pk):
    league = get_object_or_404(League, pk=pk)
    team = FantasyTeam.objects.filter(
        user=request.user,
        league=league
    )
    if len(team) == 0:
        if request.user not in league.requested_to_join.all():
            league.requested_to_join.add(request.user)
    return redirect('league_standings', pk=league.pk)

def approve_player_into_league(request, league_pk, user_pk):
    league = get_object_or_404(League, pk=league_pk)
    if request.user == league.manager:
        user = get_object_or_404(User, pk=user_pk)
        create_team_with_lineups(user, league)
        league.requested_to_join.remove(user)
    return redirect('league_standings', pk=league.pk)

def reject_player_from_league(request, league_pk, user_pk):
    league = get_object_or_404(League, pk=league_pk)
    if request.user == league.manager:
        user = get_object_or_404(User, pk=user_pk)
        league.requested_to_join.remove(user)
    return redirect('league_standings', pk=league.pk)

def remove_team_from_league(request, league_pk, team_pk):
    league = get_object_or_404(League, pk=league_pk)
    if request.user == league.manager:
        team = get_object_or_404(FantasyTeam, pk=team_pk)
        gymnasts = team.roster.all()
        for gymnast in gymnasts:
            league.drafted.remove(gymnast)
        LineUp.objects.filter(team=team).delete()
        team.delete()
    return redirect('league_standings', pk=league_pk)

class ViewFantasyTeam(DetailView):
    model = FantasyTeam
    template_name = 'core/view_team.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'team'

    def get_context_data(self, **kwargs):
        scraper = Scraper()
        context = super().get_context_data(**kwargs)
        context["roster"] = context["object"].roster.all()
        context['current_week'] = int(scraper.get_current_and_max_week(ScraperConstants.Men, datetime.now().year)['week'])
        drafted = context['object'].league.drafted.all()
        context["draftable_gymnasts"] = Gymnast.objects.exclude(id__in=drafted)
        context["lineups"] = LineUp.objects.filter(team=context['object'], week=int(scraper.get_current_and_max_week(ScraperConstants.Men, datetime.now().year)['week'])).order_by('pk')
        context['teams_competing'] = teams_competing_this_week()

        # context['averages'] = Average.objects.filter(gymnast__in=context['roster'])
        return context      

class UpdateFantasyTeam(UserPassesTestMixin, UpdateView):
    model = FantasyTeam
    form_class = NewFantasyTeamForm
    template_name = 'core/edit_team.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'team'

    def test_func(self):
        self.object = self.get_object()
        return self.request.user == self.object.user

    def form_valid(self, form):
        team = form.save(commit=False)
        team.save()
        return redirect('view_team', pk=team.pk)

def teams_competing_this_week():
    scraper = Scraper()
    # Get all weeks and their dates for the season
    weeks = scraper.get_year_weeks(ScraperConstants.Men, datetime.now().year)
    # Get date to scrape specified week
    date = [week for week in weeks if int(week['current']) == 1][0]['date']
    # Gets the schedule for the week
    schedule = scraper.get_schedule(ScraperConstants.Men, date)

    # Create a list of team names
    teams = []
    # For each day in the schedule with a meet on it
    for day in schedule:
        # For each meet on that day
        for meet in schedule[day]['meets']:
            # Create a name for the meet depending on home vs. away teams or virtual;
            if meet['away_teams'] != None:
                for team in meet['away_teams'].split(", "):
                    teams.append(team)
            if meet['home_teams'] != None:
                for team in meet['home_teams'].split(", "):
                    teams.append(team)     
    return teams

class SearchGymnasts(DetailView):
    model = FantasyTeam
    template_name = 'core/gymnast_search.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'team'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        drafted = context['object'].league.drafted.all()
        context['gymnasts'] = Gymnast.objects.all().exclude(id__in=drafted)
        context['averages'] = Average.objects.filter(gymnast__in=context['gymnasts'])
        context['events'] = ('FX', 'PH', 'SR', 'VT', 'PB', 'HB')
        context['teams_competing'] = teams_competing_this_week()
        return context

def view_gymnast(request, gymnast_pk):
    YEAR_CHOICES = {'FR' : 'Freshman', 'SO' : 'Sophomore', 'JR' : 'Junior', 'SR' : 'Senior'}    
    context = {}
    context['gymnast'] = get_object_or_404(Gymnast, pk=gymnast_pk)
    context['scores'] = Score.objects.filter(gymnast=context['gymnast'])
    context['averages'] = Average.objects.filter(gymnast=context['gymnast'])
    context['gymnast_year'] = YEAR_CHOICES[context['gymnast'].year]
    return render(request, 'core/view_gymnast.html', context)


@login_required
def myleagues(request):
    user = request.user
    context = {}
    context['leagues'] = League.objects.filter(FantasyTeam__in=FantasyTeam.objects.filter(user=user).all())
    return render(request, 'core/myleagues.html', context)

def home(request):
    gymnasts = Gymnast.objects.all()
    if request.method == 'POST':
            form = NewGymnastForm(request.POST)
            if form.is_valid():
                gymnast = form.save(commit=False)
                gymnast.save()
                return redirect('home')
    else:
        form = NewGymnastForm()
    return render(request, 'core/home.html', {'form': form, 'gymnasts' : gymnasts})

def delete_gymnast(request, pk):
    g = get_object_or_404(Gymnast, pk=pk)
    g.delete()
    return redirect('home')


