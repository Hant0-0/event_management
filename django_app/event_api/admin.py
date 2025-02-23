from django.contrib import admin

from .models import CustomUser, Event, EventParticipant


@admin.register(CustomUser)
class AdminCustomUser(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email", "is_staff", "is_superuser"]
    readonly_fields = ["password"]


@admin.register(Event)
class EvenAdmin(admin.ModelAdmin):
    list_display = ["title", "date"]


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ['event', 'member']

