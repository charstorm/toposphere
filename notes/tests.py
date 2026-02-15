from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from notes.models import Note

User = get_user_model()


class NoteTests(APITestCase):  # type: ignore[misc]
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="user@example.com", password="TestPass123")
        self.token = Token.objects.create(user=self.user)
        self.other_user = User.objects.create_user(
            email="other@example.com", password="TestPass123"
        )
        self.other_token = Token.objects.create(user=self.other_user)
        self.list_url = "/api/notes/"

    def authenticate(self, token: Token) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def create_note(self, user: Any, title: str = "Test", content: str = "Content") -> Any:
        return Note.objects.create(user=user, title=title, content=content)


class NoteCreateTests(NoteTests):
    def test_create_note_success(self) -> None:
        self.authenticate(self.token)
        data = {"title": "My Note", "content": "Note content here"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], data["title"])
        self.assertEqual(response.data["content"], data["content"])
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.first()
        assert note is not None
        self.assertEqual(note.user, self.user)

    def test_create_note_unauthenticated(self) -> None:
        data = {"title": "My Note", "content": "Content"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class NoteListTests(NoteTests):
    def test_list_notes_success(self) -> None:
        self.create_note(self.user, "Note 1", "Content 1")
        self.create_note(self.user, "Note 2", "Content 2")
        self.create_note(self.other_user, "Other Note", "Other Content")
        self.authenticate(self.token)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_list_notes_unauthenticated(self) -> None:
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_notes_ordering(self) -> None:
        note1 = self.create_note(self.user, "First", "Content")
        note2 = self.create_note(self.user, "Second", "Content")
        self.authenticate(self.token)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["id"], note2.id)
        self.assertEqual(response.data["results"][1]["id"], note1.id)


class NoteSearchTests(NoteTests):
    def test_search_by_title(self) -> None:
        self.create_note(self.user, "Python Guide", "Content")
        self.create_note(self.user, "Java Tutorial", "Content")
        self.authenticate(self.token)
        response = self.client.get(f"{self.list_url}?search=python")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Python Guide")

    def test_search_by_content(self) -> None:
        self.create_note(self.user, "Title", "Learn Python basics")
        self.create_note(self.user, "Title", "Learn Java basics")
        self.authenticate(self.token)
        response = self.client.get(f"{self.list_url}?search=python")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["content"], "Learn Python basics")

    def test_search_isolation(self) -> None:
        self.create_note(self.user, "User Note", "Content")
        self.create_note(self.other_user, "Other Note", "Content")
        self.authenticate(self.token)
        response = self.client.get(f"{self.list_url}?search=note")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)


class NoteDetailTests(NoteTests):
    def test_retrieve_note_success(self) -> None:
        note = self.create_note(self.user, "My Note", "Content")
        self.authenticate(self.token)
        response = self.client.get(f"{self.list_url}{note.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], note.title)
        self.assertEqual(response.data["content"], note.content)

    def test_retrieve_other_user_note(self) -> None:
        note = self.create_note(self.other_user, "Other Note", "Content")
        self.authenticate(self.token)
        response = self.client.get(f"{self.list_url}{note.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_unauthenticated(self) -> None:
        note = self.create_note(self.user, "Note", "Content")
        response = self.client.get(f"{self.list_url}{note.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class NoteUpdateTests(NoteTests):
    def test_update_note_success(self) -> None:
        note = self.create_note(self.user, "Old Title", "Old Content")
        self.authenticate(self.token)
        data = {"title": "New Title", "content": "New Content"}
        response = self.client.put(f"{self.list_url}{note.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        self.assertEqual(note.title, data["title"])
        self.assertEqual(note.content, data["content"])

    def test_update_other_user_note(self) -> None:
        note = self.create_note(self.other_user, "Other Title", "Content")
        self.authenticate(self.token)
        data = {"title": "New Title", "content": "New Content"}
        response = self.client.put(f"{self.list_url}{note.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_success(self) -> None:
        note = self.create_note(self.user, "Title", "Content")
        self.authenticate(self.token)
        data = {"title": "New Title"}
        response = self.client.patch(f"{self.list_url}{note.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        self.assertEqual(note.title, data["title"])
        self.assertEqual(note.content, "Content")


class NoteDeleteTests(NoteTests):
    def test_delete_note_success(self) -> None:
        note = self.create_note(self.user, "Note", "Content")
        self.authenticate(self.token)
        response = self.client.delete(f"{self.list_url}{note.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Note.objects.count(), 0)

    def test_delete_other_user_note(self) -> None:
        note = self.create_note(self.other_user, "Note", "Content")
        self.authenticate(self.token)
        response = self.client.delete(f"{self.list_url}{note.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_delete_unauthenticated(self) -> None:
        note = self.create_note(self.user, "Note", "Content")
        response = self.client.delete(f"{self.list_url}{note.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# notes/tests.py
