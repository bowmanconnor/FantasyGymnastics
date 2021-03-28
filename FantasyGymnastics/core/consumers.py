import asyncio 
import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.apps import apps


class UserConsumer(JsonWebsocketConsumer):  
    def connect(self):
        user = self.scope['user']
        print(user.username)

        if user.is_authenticated:
            # Join user group
            async_to_sync(self.channel_layer.group_add)("users_group", self.channel_name)

            # Accept connection
            self.accept()

            print("CONNECTED")

            self.update_user_status(user, True)
            # self.send_status()
        
            # Send USER_CONNECT message to group
            async_to_sync(self.channel_layer.group_send)("users_group", {
                'type': 'user_connect',
                'user_pk': user.pk,
                'username': user.username,
            })
        else:
            # Reject the connection
            self.close()
 
    def disconnect(self, code):
        # Leave user group
        async_to_sync(self.channel_layer.group_discard)("users_group", self.channel_name)
        print("DISCONNECTED")
        
        user = self.scope['user']
        print(user.username)
        if user.is_authenticated:
            self.update_user_status(user, False)
            # self.send_status()

            # Send USER_DISCONNECT message to group
            async_to_sync(self.channel_layer.group_send)("users_group", {
                'type': 'user_disconnect',
                'user_pk': user.pk,
                'username': user.username,
            })
    
 
    def send_status(self):
        users = User.objects.all()
        html_users = render_to_string("core/user_list.html", {'users': users})
        async_to_sync(self.channel_layer.group_send)(
        'users',
            {
                "type": "user_update",
                "event": "Change Status",
                "html_users": html_users
            }
        )
        
    # Receive message from websocket
    def recieve(self, text_data):
        text_data_json = json.loads(text_data)
        user_pk = text_data_json['user_pk']
        # user = self.scope['user']
        # Send message to rest of users group
        async_to_sync(self.channel_layer.group_send)("users_group", {
            'type': 'user_updated',
            'user_pk': user_pk
        })
        # async_to_sync(self.channel_layer.group_send)(self.draft_group, {
        #     'type': 'gymnast_drafted',
        #     'gymnast_pk': gymnast_pk,
        #     'gymnast_name': gymnast.name,
        #     'team_pk': team.pk,
        #     'team_name': team.name,
        #     'ncaa_team_name': gymnast.team,
        #     'position_currently_drafting': league.currently_drafting,
        # })
    
    def user_update(self, event):
        self.send_json(event)
        # print('user_update', event)
 
    def update_user_status(self, user, status):
        Profile = apps.get_model('authentication', 'Profile')
        return Profile.objects.filter(user_id = user.pk).update(status = status)

    def user_connect(self, event):
        user_pk = event['user_pk']
        username = event['username']
        self.send_json({
            'event': 'USER_CONNECT',
            'user_pk': user_pk,
            'username': username,
        })

    def user_connect(self, event):
        user_pk = event['user_pk']
        username = event['username']
        self.send_json({
            'event': 'USER_DISCONNECT',
            'user_pk': user_pk,
            'username': username,
        })
