from typing import Any

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import TodoItem, TodoList

User = get_user_model()


class TodoTests(APITestCase):  # type: ignore[misc]
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="user@example.com",
            password="TestPass123",
        )
        self.token = Token.objects.create(user=self.user)
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="TestPass123",
        )
        self.other_token = Token.objects.create(user=self.other_user)
        self.list_url = "/api/todos/"

    def authenticate(self, token: Token) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def create_todo_list(self, user: Any, title: str = "Test List") -> Any:
        return TodoList.objects.create(user=user, title=title)

    def create_todo_item(
        self,
        todo_list: Any,
        title: str = "Test Item",
        is_completed: bool = False,
    ) -> Any:
        item = TodoItem.objects.create(
            todo_list=todo_list,
            title=title,
            is_completed=is_completed,
        )
        if is_completed:
            item.completed_at = timezone.now()
            item.save()
        return item


class TodoListCreateTests(TodoTests):
    def test_create_todo_list_success(self) -> None:
        self.authenticate(self.token)
        data = {"title": "My Todo List", "description": "List description"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], data["title"])
        self.assertEqual(response.data["description"], data["description"])
        self.assertEqual(TodoList.objects.count(), 1)
        todo_list = TodoList.objects.first()
        assert todo_list is not None
        self.assertEqual(todo_list.user, self.user)

    def test_create_todo_list_unauthenticated(self) -> None:
        data = {"title": "My Todo List"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_todo_list_no_description(self) -> None:
        self.authenticate(self.token)
        data = {"title": "My List"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], data["title"])


class TodoListListTests(TodoTests):
    def test_list_todo_lists_success(self) -> None:
        self.create_todo_list(self.user, "List 1")
        self.create_todo_list(self.user, "List 2")
        self.create_todo_list(self.other_user, "Other List")
        self.authenticate(self.token)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_list_todo_lists_unauthenticated(self) -> None:
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_todo_lists_ordering(self) -> None:
        list1 = self.create_todo_list(self.user, "First")
        list2 = self.create_todo_list(self.user, "Second")
        self.authenticate(self.token)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["id"], list2.id)
        self.assertEqual(response.data["results"][1]["id"], list1.id)


class TodoListDetailTests(TodoTests):
    def test_retrieve_todo_list_success(self) -> None:
        todo_list = self.create_todo_list(self.user, "My List")
        self.authenticate(self.token)
        response = self.client.get(f"{self.list_url}{todo_list.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], todo_list.title)
        self.assertEqual(response.data["items"], [])

    def test_retrieve_todo_list_with_items(self) -> None:
        todo_list = self.create_todo_list(self.user, "My List")
        self.create_todo_item(todo_list, "Item 1")
        self.create_todo_item(todo_list, "Item 2")
        self.authenticate(self.token)
        response = self.client.get(f"{self.list_url}{todo_list.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 2)

    def test_retrieve_other_user_todo_list(self) -> None:
        todo_list = self.create_todo_list(self.other_user, "Other List")
        self.authenticate(self.token)
        response = self.client.get(f"{self.list_url}{todo_list.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TodoListUpdateTests(TodoTests):
    def test_update_todo_list_success(self) -> None:
        todo_list = self.create_todo_list(self.user, "Old Title")
        self.authenticate(self.token)
        data = {"title": "New Title", "description": "New Description"}
        response = self.client.put(
            f"{self.list_url}{todo_list.id}/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        todo_list.refresh_from_db()
        self.assertEqual(todo_list.title, data["title"])
        self.assertEqual(todo_list.description, data["description"])

    def test_partial_update_todo_list_success(self) -> None:
        todo_list = self.create_todo_list(self.user, "Title")
        self.authenticate(self.token)
        data = {"title": "New Title"}
        response = self.client.patch(
            f"{self.list_url}{todo_list.id}/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        todo_list.refresh_from_db()
        self.assertEqual(todo_list.title, data["title"])

    def test_update_other_user_todo_list(self) -> None:
        todo_list = self.create_todo_list(self.other_user, "Other Title")
        self.authenticate(self.token)
        data = {"title": "New Title"}
        response = self.client.put(
            f"{self.list_url}{todo_list.id}/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TodoListDeleteTests(TodoTests):
    def test_delete_todo_list_success(self) -> None:
        todo_list = self.create_todo_list(self.user, "My List")
        self.create_todo_item(todo_list, "Item")
        self.authenticate(self.token)
        response = self.client.delete(f"{self.list_url}{todo_list.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TodoList.objects.count(), 0)
        self.assertEqual(TodoItem.objects.count(), 0)

    def test_delete_other_user_todo_list(self) -> None:
        todo_list = self.create_todo_list(self.other_user, "Other List")
        self.authenticate(self.token)
        response = self.client.delete(f"{self.list_url}{todo_list.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(TodoList.objects.count(), 1)


class TodoItemCreateTests(TodoTests):
    def test_create_todo_item_success(self) -> None:
        todo_list = self.create_todo_list(self.user, "My List")
        self.authenticate(self.token)
        data = {"title": "My Item", "description": "Item description"}
        response = self.client.post(
            f"{self.list_url}{todo_list.id}/items/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], data["title"])
        self.assertEqual(response.data["description"], data["description"])
        self.assertEqual(TodoItem.objects.count(), 1)
        item = TodoItem.objects.first()
        assert item is not None
        self.assertEqual(item.todo_list, todo_list)
        self.assertFalse(item.is_completed)

    def test_create_todo_item_other_user_list(self) -> None:
        todo_list = self.create_todo_list(self.other_user, "Other List")
        self.authenticate(self.token)
        data = {"title": "My Item"}
        response = self.client.post(
            f"{self.list_url}{todo_list.id}/items/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_todo_item_unauthenticated(self) -> None:
        todo_list = self.create_todo_list(self.user, "My List")
        data = {"title": "My Item"}
        response = self.client.post(
            f"{self.list_url}{todo_list.id}/items/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TodoItemListTests(TodoTests):
    def test_list_todo_items_success(self) -> None:
        todo_list = self.create_todo_list(self.user, "My List")
        self.create_todo_item(todo_list, "Item 1")
        self.create_todo_item(todo_list, "Item 2")
        self.authenticate(self.token)
        response = self.client.get(f"{self.list_url}{todo_list.id}/items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_list_todo_items_isolation(self) -> None:
        todo_list1 = self.create_todo_list(self.user, "List 1")
        todo_list2 = self.create_todo_list(self.user, "List 2")
        self.create_todo_item(todo_list1, "Item 1")
        self.create_todo_item(todo_list2, "Item 2")
        self.authenticate(self.token)
        response = self.client.get(f"{self.list_url}{todo_list1.id}/items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Item 1")

    def test_list_todo_items_other_user_list(self) -> None:
        todo_list = self.create_todo_list(self.other_user, "Other List")
        self.create_todo_item(todo_list, "Item")
        self.authenticate(self.token)
        response = self.client.get(f"{self.list_url}{todo_list.id}/items/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TodoItemDetailTests(TodoTests):
    def test_retrieve_todo_item_success(self) -> None:
        todo_list = self.create_todo_list(self.user, "My List")
        item = self.create_todo_item(todo_list, "My Item")
        self.authenticate(self.token)
        response = self.client.get(f"/api/todos/items/{item.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], item.title)

    def test_retrieve_other_user_todo_item(self) -> None:
        other_list = self.create_todo_list(self.other_user, "Other List")
        item = self.create_todo_item(other_list, "Other Item")
        self.authenticate(self.token)
        response = self.client.get(f"/api/todos/items/{item.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TodoItemUpdateTests(TodoTests):
    def test_update_todo_item_success(self) -> None:
        todo_list = self.create_todo_list(self.user, "My List")
        item = self.create_todo_item(todo_list, "Old Title")
        self.authenticate(self.token)
        data = {"title": "New Title", "description": "New Description"}
        response = self.client.put(
            f"/api/todos/items/{item.id}/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.title, data["title"])
        self.assertEqual(item.description, data["description"])

    def test_mark_todo_item_complete(self) -> None:
        todo_list = self.create_todo_list(self.user, "My List")
        item = self.create_todo_item(todo_list, "My Item", is_completed=False)
        self.authenticate(self.token)
        data = {"is_completed": True}
        response = self.client.patch(
            f"/api/todos/items/{item.id}/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertTrue(item.is_completed)
        self.assertIsNotNone(item.completed_at)

    def test_mark_todo_item_incomplete(self) -> None:
        todo_list = self.create_todo_list(self.user, "My List")
        item = self.create_todo_item(todo_list, "My Item", is_completed=True)
        self.authenticate(self.token)
        data = {"is_completed": False}
        response = self.client.patch(
            f"/api/todos/items/{item.id}/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertFalse(item.is_completed)
        self.assertIsNone(item.completed_at)

    def test_partial_update_todo_item_success(self) -> None:
        todo_list = self.create_todo_list(self.user, "My List")
        item = self.create_todo_item(todo_list, "Title")
        self.authenticate(self.token)
        data = {"title": "New Title"}
        response = self.client.patch(
            f"/api/todos/items/{item.id}/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.title, data["title"])

    def test_update_other_user_todo_item(self) -> None:
        other_list = self.create_todo_list(self.other_user, "Other List")
        item = self.create_todo_item(other_list, "Other Item")
        self.authenticate(self.token)
        data = {"title": "New Title"}
        response = self.client.put(
            f"/api/todos/items/{item.id}/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TodoItemDeleteTests(TodoTests):
    def test_delete_todo_item_success(self) -> None:
        todo_list = self.create_todo_list(self.user, "My List")
        item = self.create_todo_item(todo_list, "My Item")
        self.authenticate(self.token)
        response = self.client.delete(f"/api/todos/items/{item.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TodoItem.objects.count(), 0)

    def test_delete_other_user_todo_item(self) -> None:
        other_list = self.create_todo_list(self.other_user, "Other List")
        item = self.create_todo_item(other_list, "Other Item")
        self.authenticate(self.token)
        response = self.client.delete(f"/api/todos/items/{item.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(TodoItem.objects.count(), 1)


# todos/tests.py
