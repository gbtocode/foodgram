from django.contrib import admin

from .models import Subscriber, User


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'id',
    )


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('author', 'subscriber',)


admin.site.register(User, UserAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
