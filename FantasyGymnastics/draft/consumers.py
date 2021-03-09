import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from core.models import FantasyTeam, League, Gymnast
from django.shortcuts import get_object_or_404

class DraftConsumer(WebsocketConsumer):
    def connect(self):
        # Get the league pk
        self.league_pk = self.scope['url_route']['kwargs']['league_pk']
        # Get draft group name based on the league pk
        self.draft_group = 'draft_%s' % self.league_pk

        # Check if user is in the league
        user = self.scope['user']
        is_in_league = FantasyTeam.objects.filter(league=self.league_pk, user=user).exists()

        # Only accept websocket connection if user is in league
        if is_in_league:
            # Join draft group
            async_to_sync(self.channel_layer.group_add)(self.draft_group, self.channel_name)
            self.accept()

            # Get teams in league
            teams = FantasyTeam.objects.filter(league=self.league_pk)

            draft_info = []
            for team in teams:
                draft_info.append(
                    {
                        "team_name": team.name,
                        "team_pk": team.pk,
                        "draft_position": team.draft_position,
                    }
                )

            # Get which team is currently up to draft
            currently_up_position = League.objects.filter(pk=self.league_pk).first().currently_drafting
            # Get user's team pk
            user_team_pk = FantasyTeam.objects.filter(league=self.league_pk, user=user).first().pk

            # Send draft info, which team is currently up to draft, and user's team pk
            self.send(text_data=json.dumps({'draft_info': draft_info, 'currently_up_position': currently_up_position, 'user_team_pk': user_team_pk}))
        else:
            # Reject the connection
            self.close()
    
    def disconnect(self, close_code):
        # Leave draft group
        async_to_sync(self.channel_layer.group_discard)(self.draft_group, self.channel_name)

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
            team.roster.add(gymnast)
            league = team.league
            league.drafted.add(gymnast)
            # Increment currently drafting (change to rollover or go backwards eventually)
            num_teams = len(FantasyTeam.objects.filter(league=self.league_pk))
            league.currently_drafting = (league.currently_drafting + 1) % num_teams
            league.save()

            # Send message to rest of draft group
            async_to_sync(self.channel_layer.group_send)(self.draft_group, {'type': 'draft_message', 'gymnast_pk': gymnast_pk, 'currently_up_position': league.currently_drafting})
    
    # Receive message from draft group
    def draft_message(self, event):
        gymnast_pk = event['gymnast_pk']
        currently_up_position = event['currently_up_position']
        
        # Send message to websocket
        self.send(text_data=json.dumps({'gymnast_pk_drafted': gymnast_pk, 'currently_up_position': currently_up_position}))