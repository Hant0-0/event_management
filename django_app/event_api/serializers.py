from datetime import datetime

from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from .models import Event, CustomUser, EventParticipant


class EventSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", input_formats=["%Y-%m-%d %H:%M:%S"])

    class Meta:
        model = Event
        fields = ["title", "description", "date", "location"]

    def create(self, validated_data):
        user = self.context['request'].user

        event = Event.objects.create(**validated_data)

        EventParticipant.objects.create(event=event, member=user, role="organizer")

        return event


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'password', 'email', 'is_staff']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)

        if user:
            user.set_password(password)

        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            raise AuthenticationFailed("Email and password are required.")

        try:
            user = CustomUser.objects.get(email=email)
        except ObjectDoesNotExist:
            raise AuthenticationFailed("Invalid credentials")

        if not user.check_password(password):
            raise AuthenticationFailed("Invalid credentials")

        return user


class EventParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventParticipant
        fields = '__all__'

