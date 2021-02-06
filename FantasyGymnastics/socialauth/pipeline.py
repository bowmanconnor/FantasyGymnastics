def save_profile_picture(backend, user, response, *args, **kwargs):
    print(response)
    if backend.name == 'google-oauth2':
        user.profile.picture_url = response['picture']
        user.save()
    elif backend.name == 'facebook':
        user.profile.picture_url = response['picture']['data']['url']
        user.save()