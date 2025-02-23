from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission

from .models import Event, EventParticipant


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff


class UserPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.id != view.kwargs['pk']:
            raise PermissionDenied(detail={"detail": "You can only do this with your own profile"})
        return True


class CanManageEvent(BasePermission):

    def has_permission(self, request, view):
        try:
            event = Event.objects.get(id=view.kwargs['pk'])
        except ObjectDoesNotExist:
            raise PermissionDenied({"detail": "This event does not exist"})

        try:
            user_event = EventParticipant.objects.get(event=event, member=request.user)
            if user_event:
                if user_event.role == "organizer":
                    return True
                elif user_event.role == "member":
                    raise PermissionDenied({"detail": "Participants cannot modify the event."})
        except ObjectDoesNotExist:
            return False

        return False


class CanManageEventParticipant(BasePermission):
    def has_permission(self, request, view):
        try:
            participant = EventParticipant.objects.get(id=view.kwargs['pk'])
        except ObjectDoesNotExist:
            raise PermissionError({"detail": "This event does not exist."})

        if participant.member == request.user:
            return True

        is_organizer = EventParticipant.objects.filter(event=participant.event,
                                                       role="organizer",
                                                       member=request.user).exists()
        if is_organizer:
            return True

        return False
