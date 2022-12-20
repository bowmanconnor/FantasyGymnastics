import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth.models import User
from django.apps import apps
from django.core import serializers



class UserConsumer(JsonWebsocketConsumer):

    def connect(self):
        user = self.scope['user']
        print(user.username)

        # Checks to make sure that the user is not already added to the channel group
        if user.is_authenticated and self.get_user_consumer_status(user) == False:
            # Join user group
            async_to_sync(self.channel_layer.group_add)("users_group", self.channel_name)

            Profile = apps.get_model('authentication', 'Profile')
            Profile.objects.filter(user_id = user.pk).update(consumer_status = True)
        
        # Once the user is in the group, the user should recieve updates from the group channel
        if user.is_authenticated and self.get_user_consumer_status(user) == True:

            # Accept connection
            self.accept()

            print("CONNECTED")

            async_to_sync(self.channel_layer.group_send)("users_group", {
                'type': 'user_updated',
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
 

    '''
    # Removes the user from the channel group. Currently relies on timeout of user to remove from group
    # Would like to association this disconnect function with when the user logs off
    def disconnect(self, code):
        user = self.scope['user']
        print(user.username)

        # Leave user group
        if user.is_authenticated and self.get_user_consumer_status(user) == True:
            async_to_sync(self.channel_layer.group_discard)("users_group", self.channel_name)
            Profile = apps.get_model('authentication', 'Profile')
            Profile.objects.filter(user_id = user.pk).update(consumer_status = False)
            print("DISCONNECTED")
        
        if user.is_authenticated:
            # self.update_user_status(user, False)

            # Send USER_DISCONNECT message to group
            # async_to_sync(self.channel_layer.group_send)("users_group", {
            #     'type': 'user_disconnect',
            #     'user_pk': user.pk,
            #     'username': user.username,
            #     'status': False
            # })
            async_to_sync(self.channel_layer.group_send)("users_group", {
                'type': 'user_updated',
                'user_pk': user.pk,
                'username': user.username,
                'status': False
            })
    '''
    
        
    # Receive message from websocket
    def recieve(self, text_data):
        text_data_json = json.loads(text_data)
        user_pk = text_data_json['user_pk']
        username = text_data_json['username']
        status = text_data_json['status']
        # Send message to rest of users group
        async_to_sync(self.channel_layer.group_send)("users_group", {
            'type': 'user_updated',
            'user_pk': user_pk,
            'username': username,
            'status': status
        })

    
    # Receive message from users group
    def user_updated(self, event):
        self.send(text_data=json.dumps({
            'event': 'USER_UPDATED',
            'user_pk': event['user_pk'],
            'username': event['username'],
            'status': event['status']
        }))
    
    
    # Return user online status
    def get_user_consumer_status(self, user):
        if user.is_authenticated:
            user_pk = user.pk
            Profile = apps.get_model('authentication', 'Profile')
            user_conusmer_status = Profile.objects.filter(user_id = user_pk).first().consumer_status
            return user_conusmer_status


