import asyncio 
import json
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import Profile
from django.contrib.auth.models import User
from django.template.loader import render_to_string


class UserConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print('connect')
        await self.accept()

        # Join users group
        await self.channel_layer.group_add("users", self.channel_name)

        user = self.scope['user']
        if user.is_authenticated:
            await self.update_user_status(user, True)
            await self.send_status()

    async def disconnect(self):
        # Leave users group
        await self.channel_layer.group_discard("users", self.channel_name)
        
        user = self.scope['user']
        if user.is_authenticated:
            await self.update_user_status(user, False)
            await self.send_status()
    
    async def send_status (self):
        users = User.objects.all()
        html_users = render_to_string("includes/users.html", {'users': users})
        await self.channel_layer.group_send(
            'users',
            {
                "type": "user_update",
                "event": "Change Status",
                "html_users": html_users
            }
        )
    
    async def user_update (self, event):
        await self.send_json(event)
        print('user_update', event)

    @database_sync_to_async
    def update_user_status(self, user, status):
        if status == True:
            status_text = "Online"
        else:
            status_text = "Offline"
        Profile.objects.filter(user_id = user.pk).update(status_text = status_text)
        return Profile.objects.filter(user_id = user.pk).update(status = status)