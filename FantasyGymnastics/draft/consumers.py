import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from core.models import FantasyTeam

class DraftConsumer(WebsocketConsumer):
    def connect(self):
        # Get the league pk
        self.league_pk = self.scope['url_route']['kwargs']['league_pk']
        # Create a draft group based on the league pk
        self.draft_group = 'draft_%s' % self.league_pk

        # Check if user is in the league
        user = self.scope['user']
        is_in_league = FantasyTeam.objects.filter(league=self.league_pk, user=user).exists()

        # Join draft group
        async_to_sync(self.channel_layer.group_add)(self.draft_group, self.channel_name)

        # Only accept websocket connection if user is in league
        if is_in_league:
            self.accept()
        else:
            # Reject the connection
            self.close()
    
    def disconnect(self, close_code):
        # Leave draft group
        async_to_sync(self.channel_layer.group_discard)(self.draft_group, self.channel_name)

    # Receive message from websocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to rest of draft group
        async_to_sync(self.channel_layer.group_send)(self.draft_group, {'type': 'draft_message', 'message': message})
    
    # Receive message from draft group
    def draft_message(self, event):
        message = event['message']

        # Send message to websocket
        self.send(text_data=json.dumps({'message': message}))