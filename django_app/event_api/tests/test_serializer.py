from datetime import datetime
import pytest
from rest_framework.test import APIClient
from event_api.models import CustomUser, Event, EventParticipant


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def make_user(email="test@gmail.com", first_name="Oleg", last_name="Ivanov", password="TtppZZffd2"):
        user = CustomUser.objects.create(
            email=email, first_name=first_name, last_name=last_name
        )
        user.set_password(password)
        user.save()
        return user
    return make_user


@pytest.fixture
def create_event(db):
    def make_event(title="Daily meeting", description="Discussion of a new project",
                   date="12-02-2025 14:00:00", location="Kiev"):
        parsed_date = datetime.strptime(date, "%d-%m-%Y %H:%M:%S")
        event = Event.objects.create(
            title=title, description=description, date=parsed_date, location=location
        )
        return event
    return make_event


@pytest.fixture
def create_event_participant(db):
    def add_participant(event, member, role):
        return EventParticipant.objects.create(event=event, member=member, role=role)
    return add_participant


@pytest.mark.django_db
class TestUser:
    @pytest.mark.parametrize(
        "email, first_name, last_name, password",
        [("test@gmail.com", "Oleg", "Ivanov", "TzH77RgaaA")]
    )
    def test_user_registration(self, api_client, email, first_name, last_name, password):
        response = api_client.post(
            "/api/register/", {"email": email, "first_name": first_name, "last_name": last_name, "password": password}
        )
        assert response.status_code == 201
        assert "email" in response.data

    def test_login_user(self, api_client, create_user):
        user = create_user()
        response = api_client.post(
            "/api/login/", {"email": user.email, "password": "TtppZZffd2"}
        )
        assert response.status_code == 200
        assert "access" in response.data


@pytest.mark.django_db
class TestEvent:
    def test_event_list(self, api_client, create_user):
        user = create_user()
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/events/")
        assert response.status_code == 200

    def test_event_create(self, api_client, create_user):
        user = create_user()
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/events/", {
                "title": "Daily meeting",
                "description": "Discussion of a new project",
                "date": "2025-02-12 14:00:00",
                "location": "Kiev"
            }
        )
        assert response.status_code == 201

    def test_event_detail(self, api_client, create_user, create_event, create_event_participant):
        user = create_user()
        event = create_event()
        create_event_participant(event, user, "organizer")
        api_client.force_authenticate(user=user)
        response = api_client.get(f"/api/event/{event.id}/")
        assert response.status_code == 200

    def test_event_update(self, api_client, create_user, create_event, create_event_participant):
        user = create_user()
        event = create_event()
        create_event_participant(event, user, "organizer")
        api_client.force_authenticate(user=user)
        response = api_client.put(
            f"/api/event/{event.id}/", {
                "title": "Updated meeting",
                "description": event.description,
                "date": event.date,
                "location": event.location,
            }
        )
        assert response.status_code == 200

    def test_event_delete(self, api_client, create_user, create_event, create_event_participant):
        user = create_user()
        event = create_event()
        create_event_participant(event, user, "organizer")
        api_client.force_authenticate(user=user)
        response = api_client.delete(f"/api/event/{event.id}/")
        assert response.status_code == 204


@pytest.mark.django_db
class TestParticipant:
    def test_participant_list(self, api_client, create_user):
        user = create_user()
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/participants/")
        assert response.status_code == 200

    def test_participant_create(self, api_client, create_user, create_event):
        user = create_user()
        event = create_event()
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/participants/", {"event": event.id, "member": user.id, "role": "member"}
        )
        assert response.status_code == 201

    def test_update_participant_role_as_organizer(self, api_client, create_user, create_event, create_event_participant):
        user_organizer = create_user()
        event = create_event()
        create_event_participant(event, user_organizer, "organizer")

        user_member_1 = create_user(email="test2@gmail.com", first_name="Stas", last_name="Stasov", password="Ttzzfdsf23")

        participant_member_1 = create_event_participant(event, user_member_1, "member")

        api_client.force_authenticate(user=user_organizer)
        response = api_client.put(
            f"/api/participants/{participant_member_1.id}/", {
                "event": event.id,
                "member": user_member_1.id,
                "role": "organizer"
            }
        )
        assert response.status_code == 200

    def test_update_participant_role_as_non_organizer(self, api_client, create_user, create_event, create_event_participant):
        user_organizer = create_user()
        event = create_event()
        create_event_participant(event, user_organizer, "organizer")

        user_member_1 = create_user(email="test2@gmail.com", first_name="Stas", last_name="Stasov", password="Ttzzfdsf23")
        user_member_2 = create_user(email="test3@gmail.com", first_name="Max", last_name="Manoilo", password="Ttzzfdsf23")

        create_event_participant(event, user_member_1, "member")
        participant_member_2 = create_event_participant(event, user_member_2, "member")

        api_client.force_authenticate(user=user_member_1)
        response = api_client.put(
            f"/api/participants/{participant_member_2.id}/", {
                "event": event.id,
                "member": user_member_2.id,
                "role": "organizer"
            }
        )
        assert response.status_code == 403

    def test_participant_delete_role_as_organizer(self, api_client, create_user, create_event, create_event_participant):
        user_organizer = create_user()
        event = create_event()
        create_event_participant(event, user_organizer, "organizer")

        user_member_1 = create_user(email="test2@gmail.com", first_name="Stas", last_name="Stasov", password="Ttzzfdsf23")

        participant_member_1 = create_event_participant(event, user_member_1, "member")

        api_client.force_authenticate(user=user_organizer)

        response = api_client.delete(
            f"/api/participants/{participant_member_1.id}/"
        )
        assert response.status_code == 204


    def test_participant_delete_role_as_non_organizer(self, api_client, create_user, create_event, create_event_participant):
        user_organizer = create_user()
        event = create_event()
        create_event_participant(event, user_organizer, "organizer")

        user_member_1 = create_user(email="test2@gmail.com", first_name="Stas", last_name="Stasov", password="Ttzzfdsf23")
        user_member_2 = create_user(email="test3@gmail.com", first_name="Max", last_name="Manoilo", password="Ttzzfdsf23")

        create_event_participant(event, user_member_1, "member")
        participant_member_2 = create_event_participant(event, user_member_2, "member")

        api_client.force_authenticate(user=user_member_1)
        response = api_client.delete(f"/api/participants/{participant_member_2.id}/")
        assert response.status_code == 403

