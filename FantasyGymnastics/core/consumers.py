import asyncio 
import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.apps import apps
from django.core import serializers


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
        
            # Send USER_CONNECT message to group
            async_to_sync(self.channel_layer.group_send)("users_group", {
                'type': 'user_connect',
                'user_pk': user.pk,
                'username': user.username,
                'status': True
            })

            users_qset = User.objects.all()
            users = []
            Profile = apps.get_model('authentication', 'Profile')
            # Create json of all users' pk and profile online status
            for user_model_object in users_qset:
                user_pk = user_model_object.pk
                user_online_status = Profile.objects.filter(user_id = user_pk).first().status
                user_json = json.loads(serializers.serialize('json', [user_model_object]))[0]
                user_json['user_pk'] = user_pk
                user_json['status'] = user_online_status
                users.append(user_json)
            
            # Send all users to the client to update all other users' statuses
            self.send(text_data=json.dumps({
                'event': 'SYNC',
                'users': users
            }))
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
                'status': False
            })
    
        
    # Receive message from websocket
    def recieve(self, text_data):
        text_data_json = json.loads(text_data)
        user_pk = text_data_json['user_pk']
        status = text_data_json['status']
        # user = self.scope['user']
        # Send message to rest of users group
        async_to_sync(self.channel_layer.group_send)("users_group", {
            'type': 'user_updated',
            'user_pk': user_pk,
            'status': status
        })

    
    # Receive message from users group
    def user_updated(self, event):
        self.send(text_data=json.dumps({
            'event': 'USER_UPDATED',
            'user_pk': event['user_pk'],
            'status': event['status']
        }))
    

    def user_update(self, event):
        self.send_json(event)
        # print('user_update', event)
 

    def update_user_status(self, user, status):
        Profile = apps.get_model('authentication', 'Profile')
        Profile.objects.filter(user_id = user.pk).update(status = status)


    def user_connect(self, event):
        user_pk = event['user_pk']
        username = event['username']
        self.send_json({
            'event': 'USER_CONNECT',
            'user_pk': user_pk,
            'username': username,
        })


    def user_disconnect(self, event):
        user_pk = event['user_pk']
        username = event['username']
        self.send_json({
            'event': 'USER_DISCONNECT',
            'user_pk': user_pk,
            'username': username,
        })
