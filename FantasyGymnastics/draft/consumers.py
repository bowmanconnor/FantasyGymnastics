import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from core.models import FantasyTeam, League, Gymnast, LineUp
from django.shortcuts import get_object_or_404
from django.core import serializers
from scraper.Scraper import Scraper, ScraperConstants
from django.core.management import call_command
from .matchups import round_robin_matchups
import datetime
from weekly_gameplay.models import Matchup

class DraftConsumer(WebsocketConsumer):
    def connect(self):
        # Get the league pk
        self.league_pk = self.scope['url_route']['kwargs']['league_pk']
        # Get draft group name based on the league pk
        self.draft_group = 'draft_%s' % self.league_pk

        # Check if user is in the league
        user = self.scope['user']
        team = FantasyTeam.objects.filter(league=self.league_pk, user=user).first()
        is_in_league = not team is None

        # Only accept websocket connection if user is in league
        if is_in_league:
            # Join draft group
            async_to_sync(self.channel_layer.group_add)(self.draft_group, self.channel_name)
            # Set team status to in draft
            team.currently_in_draft = True
            team.save()

            # Accept connection
            self.accept()

            # Send TEAM_JOIN message to group
            async_to_sync(self.channel_layer.group_send)(self.draft_group, {
                'type': 'team_connect',
                'team_pk': team.pk,
                'team_name': team.name,
            })



            # Get teams in league
            teams_qset = FantasyTeam.objects.filter(league=self.league_pk)
            teams = []
            for team_model_object in teams_qset:
                roster = json.loads(serializers.serialize('json', team_model_object.roster.all()))
                team_json = json.loads(serializers.serialize('json', [team_model_object]))[0]
                team_json['fields']['roster'] = roster
                teams.append(team_json)

            # Get which team is currently up to draft
            position_currently_drafting = League.objects.filter(pk=self.league_pk).first().currently_drafting

            # Send draft info, which team is currently up to draft, and user's team pk
            self.send(text_data=json.dumps({
                'event': 'SYNC',
                'user_team_pk': team.pk,
                'position_currently_drafting': position_currently_drafting,
                'teams': teams,
            }))
        else:
            # Reject the connection
            self.close()
    
    def disconnect(self, close_code):
        # Leave draft group
        async_to_sync(self.channel_layer.group_discard)(self.draft_group, self.channel_name)

        # Set team status to not in draft
        team = FantasyTeam.objects.filter(league=self.league_pk, user=self.scope['user']).first()
        team.currently_in_draft = False
        team.save()

        # Send TEAM_DISCONNECT message to group
        async_to_sync(self.channel_layer.group_send)(self.draft_group, {
            'type': 'team_disconnect',
            'team_pk': team.pk,
            'team_name': team.name,
        })
    
    # Receive message from websocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        gymnast_pk = text_data_json['gymnast_pk']
        user = self.scope['user']
        # Get league
        league = League.objects.filter(pk=self.league_pk).first()
        # Get user's team
        team = FantasyTeam.objects.filter(user=user, league=self.league_pk).first()
        
        # Get the position that is up to draft
        currently_drafting = league.currently_drafting
        # Check if user who send draft request is currently up
        if team.draft_position == currently_drafting and not league.draft_complete and league.draft_started:
            # Do something here with the gymnast_pk and the team
            gymnast = get_object_or_404(Gymnast, pk=gymnast_pk)
            if gymnast not in league.drafted.all() and len(team.roster.all()) < league.roster_size:
                team.roster.add(gymnast)
                league = team.league
                league.drafted.add(gymnast)

                # Snake draft, initially going down
                num_teams = len(FantasyTeam.objects.filter(league=self.league_pk))
                if league.going_down:
                    # If last person is drafting
                    if league.currently_drafting == (num_teams - 1):
                        # Give them another turn and start going up
                        league.going_down = False
                    else:
                        league.currently_drafting = league.currently_drafting + 1
                else:
                    # If first person is drafting on way back up
                    if league.currently_drafting == 0:
                        # Give first person another chance and start going down
                        league.going_down = True
                    else:
                        league.currently_drafting = league.currently_drafting - 1
                league.save()

                if len(league.drafted.all()) == league.roster_size * num_teams:
                    # Drafting is done
                    scraper = Scraper()
                    year = datetime.date.today().year
                    num_weeks = int(scraper.get_current_and_max_week(ScraperConstants.Men, year)['max'])
                    matchups = round_robin_matchups(num_teams, num_weeks)
                    team_pks = [x.pk for x in list(FantasyTeam.objects.filter(league__pk=self.league_pk))]
                    # Creates matchups for entire season
                    for week in matchups:
                        for matchup in matchups[week]:
                            team1_pk = team_pks[matchup[0] - 1]
                            team2_pk = team_pks[matchup[1] - 1]
                            team1 = FantasyTeam.objects.filter(pk=team1_pk).first()
                            team2 = FantasyTeam.objects.filter(pk=team2_pk).first()
                            m = Matchup(team1=team1, team2=team2, league=league, week=week)
                            m.save()
                            # Creates lineups for entire season
                            events = ['FX', 'PH', 'SR', 'VT', 'PB', 'HB']
                            for i in range(6):
                                if not LineUp.objects.filter(team=team1, event=events[i], week=week).exists():
                                    LineUp.objects.create(team=team1, event=events[i], week=week)
                                if not LineUp.objects.filter(team=team2, event=events[i], week=week).exists():
                                    LineUp.objects.create(team=team2, event=events[i], week=week)
  

                    league.draft_complete = True
                    async_to_sync(self.channel_layer.group_send)(self.draft_group, {
                        'type': 'draft_complete',
                    })

                # PERFORM CHECK AND AUTO DRAFT HERE
                league.save()

                # Send message to rest of draft group
                async_to_sync(self.channel_layer.group_send)(self.draft_group, {
                    'type': 'gymnast_drafted',
                    'gymnast_pk': gymnast_pk,
                    'gymnast_name': gymnast.name,
                    'team_pk': team.pk,
                    'team_name': team.name,
                    'ncaa_team_name': gymnast.team,
                    'position_currently_drafting': league.currently_drafting,
                })
            else:
                print("DRAFTING ERROR")
                async_to_sync(self.channel_layer.group_send)(self.draft_group, {
                    'type': 'gymnast_draft_error',
                    'error': 'Gymnast has already been drafted'
                })
        else:
            async_to_sync(self.channel_layer.group_send)(self.draft_group, {
                'type': 'gymnast_draft_error',
                'error': 'Not your turn to draft'
            })
    
    def team_connect(self, event):
        team_pk = event['team_pk']
        team_name = event['team_name']
        self.send(text_data=json.dumps({
            'event': 'TEAM_CONNECT',
            'team_pk': team_pk,
            'team_name': team_name,
        }))

    def team_disconnect(self, event):
        team_pk = event['team_pk']
        team_name = event['team_name']
        self.send(text_data=json.dumps({
            'event': 'TEAM_DISCONNECT',
            'team_pk': team_pk,
            'team_name': team_name,
        }))

    def gymnast_drafted(self, event):
        # Send message to consumer
        self.send(text_data=json.dumps({
            'event': 'GYMNAST_DRAFTED',
            'ncaa_team_name': event['ncaa_team_name'],
            'team_pk': event['team_pk'],
            'team_name': event['team_name'],
            'gymnast_pk': event['gymnast_pk'],
            'gymnast_name': event['gymnast_name'],
            'position_currently_drafting': event['position_currently_drafting'],
        }))
    
    def gymnast_draft_error(self, event):
        self.send(text_data=json.dumps({
            'event': 'GYMNAST_DRAFT_ERROR',
            'error': event['error'],
        }))

    def draft_complete(self, event):
        self.send(text_data=json.dumps({
            'event': 'DRAFT_COMPLETE'
        }))