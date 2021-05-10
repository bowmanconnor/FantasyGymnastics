from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import League, FantasyTeam, Gymnast, LineUp, Score, ContactUs, Post
from django.views.generic import UpdateView, DetailView, DeleteView, ListView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from scraper.Scraper import ScraperConstants
from scraper.Scraper import Scraper
import datetime
from weekly_gameplay.models import Average, Matchup
from django.db.models import Q
from .forms import NewLeagueForm, NewFantasyTeamForm, NewGymnastForm, ContactUsForm
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from pytz import timezone
from django.http import HttpResponse
import base64


#Helper Function
def create_team(user, league):
    scraper = Scraper()
    team = FantasyTeam.objects.create(
        user=user,
        league=league,
        name=str(user.username)+"'s Team")
        
@login_required
def create_league(request):
    if request.method == 'POST':
        form = NewLeagueForm(request.POST)
        if form.is_valid():
            league = form.save(commit=False)
            league.manager = request.user
            league.save()
            create_team(request.user, league)
            return redirect('league_standings', pk=league.pk)
    else:
        form = NewLeagueForm()
    return render(request, 'core/create_league.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class LeagueStandings(DetailView):
    model = League
    template_name = 'core/league_standings.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'league'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teams'] = FantasyTeam.objects.filter(league_id=context['object'].id).order_by('-wins', 'name')
        scraper = Scraper()
        context['current_week'] = int(scraper.get_current_and_max_week(ScraperConstants.Men, datetime.datetime.now().year)['week'])
        context['max_week'] = int(scraper.get_current_and_max_week(ScraperConstants.Men, datetime.datetime.now().year)['max'])
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
        if request.user not in league.requested_to_join.all() and not league.draft_started:
            league.requested_to_join.add(request.user)
    return redirect('league_standings', pk=league.pk)

@login_required
def approve_player_into_league(request, league_pk, user_pk):
    league = get_object_or_404(League, pk=league_pk)
    if request.user == league.manager and not league.draft_started:
        user = get_object_or_404(User, pk=user_pk)
        create_team(user, league)
        league.requested_to_join.remove(user)
    return redirect('league_standings', pk=league.pk)

@login_required
def reject_player_from_league(request, league_pk, user_pk):
    league = get_object_or_404(League, pk=league_pk)
    if request.user == league.manager:
        user = get_object_or_404(User, pk=user_pk)
        league.requested_to_join.remove(user)
    return redirect('league_standings', pk=league.pk)

@login_required
def remove_team_from_league(request, league_pk, team_pk):
    league = get_object_or_404(League, pk=league_pk)
    if request.user == league.manager and not league.draft_started:
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
        context['current_week'] = int(scraper.get_current_and_max_week(ScraperConstants.Men, datetime.datetime.now().year)['week'])
        context["lineups"] = LineUp.objects.filter(team=context['object'], week=context['current_week']).order_by('pk')
        context['teams_competing'] = teams_competing_this_week()

        context['meet_started'] = {} #Could this be optimized?
        weeks = scraper.get_year_weeks(ScraperConstants.Men, datetime.datetime.now().year)

        # Fixes index error once in post season
        try:
            date = [week for week in weeks if int(week['wk']) == context['current_week']][0]['date']
        except IndexError:
            return context
            
        schedule = scraper.get_schedule(ScraperConstants.Men, date)
        gymnasts = context["roster"]
        # Loops through every meet day this week
        for day in schedule:
            # Loops through every meet on day
            for meet in schedule[day]['meets']:
                # Loops through gymnasts 
                for gymnast in gymnasts: #Could this be optimized?
                    # Checks if gymnasts team is in this meet
                    if gymnast.team in str(meet['home_teams']) or gymnast.team in str(meet['away_teams']): #Could this be optimized?
                        # Checks if this is gymnasts first meet of week
                        if gymnast.name not in context['meet_started']:
                            # Meet start datetime
                            meet_datetime = datetime.datetime.strptime(str(meet['d']) + " " + str(meet['time']), "%Y-%m-%d %H:%M:%S")
                            # Current datetime (eastern because thats what RTN uses)
                            now = datetime.datetime.now(timezone('US/Eastern'))
                            if now.date() > meet_datetime.date():
                                context['meet_started'][gymnast.name] = True
                            elif now.date() == meet_datetime.date():
                                if meet_datetime.time() != datetime.time(0, 0, 0):
                                    if now.time() > meet_datetime.time():
                                        context['meet_started'][gymnast.name] = True
                                    else:
                                        context['meet_started'][gymnast.name] = False
                                else:
                                    if now.time() >= datetime.time(12, 0, 0):
                                        context['meet_started'][gymnast.name] = True
                                    else: 
                                        context['meet_started'][gymnast.name] = False
                            else:
                                context['meet_started'][gymnast.name] = False
                        
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
    # Create a list of team names
    teams = []

    # Get all weeks and their dates for the season
    scraper = Scraper()
    weeks = scraper.get_year_weeks(ScraperConstants.Men, datetime.datetime.now().year)
    # Get date to scrape this week
    # Fixes index error once in post season
    try:
        date = [week for week in weeks if int(week['current']) == 1][0]['date']
    except IndexError:
        return teams
    # Gets the schedule for this week
    schedule = scraper.get_schedule(ScraperConstants.Men, date)

   
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
    posts = Post.objects.all()
    gymnasts = Gymnast.objects.all()
    if request.method == 'POST':
            form = NewGymnastForm(request.POST)
            if form.is_valid():
                gymnast = form.save(commit=False)
                gymnast.save()
                return redirect('home')
    else:
        form = NewGymnastForm()
    return render(request, 'core/home.html', {'form': form, 'gymnasts' : gymnasts, 'posts' : posts})

def delete_league(request, pk):
    league = get_object_or_404(League, pk=pk)
    if request.user == league.manager:
        league.delete()
    return redirect('myleagues')

def how_to_play(request):
    return render(request, 'core/how_to_play.html')

@login_required
def cutter(request):
    return render(request, 'core/cutter.html')
  
@login_required
def contact_us(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            contact_us = form.save(commit=False)
            contact_us.user = request.user
            contact_us.save()
            return redirect('contact_us_done')
    else:
        form = ContactUsForm()
    return render(request, 'core/contact_us.html', {'form': form})

def contact_us_done(request):
    return render(request, 'core/contact_us_done.html')

class PostList(ListView):
    queryset = Post.objects.filter(status=1).order_by('-posted_at')
    template_name = 'news/news.html'
    paginate_by = 10
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class PostDetail(DetailView):
    model = Post
    template_name = 'news/post_detail.html'

def weekly_news(request):
    context = {}
    scraper = Scraper()
    context['current_week'] = int(scraper.get_current_and_max_week(ScraperConstants.Men, datetime.datetime.now().year)['week'])
    context['posts'] = Post.objects.filter(status=1, week=context['current_week']).order_by('-posted_at')
    context['lineup'] = 0
    context['platform'] = 1
    template_name = 'news/weekly_news.html'
    return render(request, 'news/weekly_news.html', context)

@staff_member_required
def view_contact_us(request):
    context = {}
    context['feedback'] = ContactUs.objects.all()
    return render(request, 'core/view_contact_us.html', context)

@staff_member_required
def delete_contact_us(request, pk):
    responce = get_object_or_404(ContactUs, pk=pk)
    responce.delete()
    return redirect('view_contact_us')


def drawbot(request):
    return render(request, 'core/drawbot.html')

def drawbot_send(request):
    if request.method == 'POST':
        if 'image' in request.POST:
            image = request.POST['image']
            print("Received image")
            with open('canvas_drawing.png', 'wb') as f:
                f.write(base64.b64decode(image[22:]))
            return HttpResponse('success') # if everything is OK
    # nothing went well
    return HttpResponse('FAIL!!!!!')