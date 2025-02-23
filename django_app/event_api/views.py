from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import EventParticipantFilter
from .models import CustomUser, Event, EventParticipant
from .permissions import IsStaff, UserPermission, CanManageEvent, CanManageEventParticipant
from .serializers import UserSerializer, UserLoginSerializer, EventSerializer, EventParticipantSerializer
from .tasks import message_for_register_event

class UserRegisterAPIView(APIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(
        request_body=UserSerializer,
    )
    def post(self, request):
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListUsersAPIView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsStaff]
    filter_backends = [DjangoFilterBackend, SearchFilter]

    filterset_fields = ["email", "first_name", "last_name"]
    search_fields = ["email", "first_name", "last_name"]


class UserLoginAPIView(APIView):

    @swagger_auto_schema(
        request_body=UserLoginSerializer,
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserLoginSerializer(data=data)

        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({"refresh": str(refresh),
                             "access": str(refresh.access_token)})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, UserPermission]


class EventListAPIView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]

    filterset_fields = ["title", "location"]
    search_fields = ["title", "location"]


class EventAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, CanManageEvent]


class EventParticipantListAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = EventParticipantFilter
    search_fields = ["event__title", "member__email", "role"]

    def get_queryset(self):
        return EventParticipant.objects.all()

    def get_serializer(self, *args, **kwargs):
        return EventParticipantSerializer(*args, **kwargs)

    @swagger_auto_schema(
        request_body=EventParticipantSerializer,
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EventParticipantSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = EventParticipantSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=EventParticipantSerializer,
        responses={200: openapi.Response("Successful entrance")}
    )
    def create(self, request, *args, **kwargs):
        data = request.data

        event_pat = EventParticipant.objects.filter(event=data['event'],
                                                    member=data['member']).exists()
        if event_pat:
            return Response({"detail": "You are already registered for this event."})

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        if serializer.data["role"] == "member":
            full_name = f"{self.request.user.first_name} + {self.request.user.last_name}"
            date_event = Event.objects.get(id=serializer.data["event"]).date
            message_for_register_event.delay(self.request.user.email, full_name, date_event)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class EventParticipantDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EventParticipant
    serializer_class = EventParticipantSerializer
    permission_classes = [IsAuthenticated, CanManageEventParticipant]












