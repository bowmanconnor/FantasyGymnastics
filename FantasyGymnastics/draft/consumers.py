import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from core.models import FantasyTeam, League, Gymnast
from django.shortcuts import get_object_or_404
from django.core import serializers

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
                'teams': teams
            }))
        else:
            # Reject the connection
            self.close()
    
    def disconnect(self, close_code):
        print('DISCONNECT')
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
        if team.draft_position == currently_drafting:
            # Do something here with the gymnast_pk and the team
            gymnast = get_object_or_404(Gymnast, pk=gymnast_pk)
            if gymnast not in league.drafted.all():
                print("DRAFTED")
                team.roster.add(gymnast)
                league = team.league
                league.drafted.add(gymnast)
                # Increment currently drafting (change to rollover or go backwards eventually)
                num_teams = len(FantasyTeam.objects.filter(league=self.league_pk))
                league.currently_drafting = (league.currently_drafting + 1) % num_teams
                league.save()

                # Send message to rest of draft group
                async_to_sync(self.channel_layer.group_send)(self.draft_group, {
                    'type': 'gymnast_drafted',
                    'gymnast_pk': gymnast_pk,
                    'gymnast_name': gymnast.name,
                    'team_pk': team.pk,
                    'position_currently_drafting': league.currently_drafting
                })
            else:
                print("DRAFTING ERROR")
                async_to_sync(self.channel_layer.group_send)(self.draft_group, {
                    'type': 'gymnast_draft_error',
                    'error': 'Gymnast has already been drafted'
                })
    
    def team_connect(self, event):
        team_pk = event['team_pk']
        self.send(text_data=json.dumps({
            'event': 'TEAM_CONNECT',
            'team_pk': team_pk
        }))

    def team_disconnect(self, event):
        team_pk = event['team_pk']
        self.send(text_data=json.dumps({
            'event': 'TEAM_DISCONNECT',
            'team_pk': team_pk
        }))

    def gymnast_drafted(self, event):
        # Send message to consumer
        self.send(text_data=json.dumps({
            'event': 'GYMNAST_DRAFTED',
            'team_pk': event['team_pk'],
            'gymnast_pk': event['gymnast_pk'],
            'gymnast_name': event['gymnast_name'],
            'position_currently_drafting': event['position_currently_drafting'],
        }))
    
    def gymnast_draft_error(self, event):
        self.send(text_data=json.dumps({
            'event': 'GYMNAST_DRAFT_ERROR',
            'error': event['error'],
        }))