from django.contrib.auth import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.apps import apps
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@receiver(user_logged_in)
def on_user_login(sender, **kwargs):
    # Set user profile online status to true
    user = kwargs.get('user')
    Profile = apps.get_model('authentication', 'Profile')
    Profile.objects.filter(user_id = user.pk).update(status = True)
    Profile.objects.filter(user_id = user.pk).update(consumer_status = False)
    send_update_user_status_signal(user, True)


@receiver(user_logged_out)
def on_user_logout(sender, **kwargs):
    # Set user profile online status to false
    user = kwargs.get('user')
    Profile = apps.get_model('authentication', 'Profile')
    Profile.objects.filter(user_id = user.pk).update(status = False)
    send_update_user_status_signal(user, False)


def send_update_user_status_signal(user, status):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("users_group", {
        'type': 'user_updated',
        'user_pk': user.pk,
        'username': user.username,
        'status': status
    })