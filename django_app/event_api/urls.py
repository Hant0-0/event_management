from django.urls import path

from .views import UserRegisterAPIView, ListUsersAPIView, UserLoginAPIView, UserAPIView, EventListAPIView, EventAPIView, EventParticipantListAPIView, \
    EventParticipantDetailAPIView

urlpatterns = [

    path("register/", UserRegisterAPIView.as_view()),
    path("login/", UserLoginAPIView.as_view()),
    path("list_users/", ListUsersAPIView.as_view()),
    path("user/<int:pk>/", UserAPIView.as_view()),

    path("events/", EventListAPIView.as_view()),
    path("event/<int:pk>/", EventAPIView.as_view()),

    path("participants/", EventParticipantListAPIView.as_view()),
    path("participants/<int:pk>/", EventParticipantDetailAPIView.as_view()),



]