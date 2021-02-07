from django.contrib import admin
from .models import Profile

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    fields = ['user', 'picture_url']

admin.site.register(Profile, ProfileAdmin)