from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import UserProfile, Contact


class UserAdmin(admin.ModelAdmin):
    search_fields = ['username']


admin.site.register(get_user_model(), UserAdmin)
admin.site.register(UserProfile)
admin.site.register(Contact)
