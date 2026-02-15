from typing import Any

from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound

from .models import TodoItem, TodoList
from .serializers import TodoItemSerializer, TodoListSerializer


class TodoListListCreateView(generics.ListCreateAPIView):  # type: ignore[misc]
    serializer_class = TodoListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        return TodoList.objects.filter(user=self.request.user)

    def perform_create(self, serializer: TodoListSerializer) -> None:
        serializer.save(user=self.request.user)


class TodoListDetailView(generics.RetrieveUpdateDestroyAPIView):  # type: ignore[misc]
    serializer_class = TodoListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        return TodoList.objects.filter(user=self.request.user)


class TodoItemListCreateView(generics.ListCreateAPIView):  # type: ignore[misc]
    serializer_class = TodoItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_todo_list(self) -> TodoList:
        try:
            return TodoList.objects.get(  # type: ignore[no-any-return]
                pk=self.kwargs["list_id"],
                user=self.request.user,
            )
        except TodoList.DoesNotExist:
            raise NotFound("Todo list not found.")

    def get_queryset(self) -> Any:
        todo_list = self.get_todo_list()
        return TodoItem.objects.filter(todo_list=todo_list)

    def perform_create(self, serializer: TodoItemSerializer) -> None:
        todo_list = self.get_todo_list()
        serializer.save(todo_list=todo_list)


class TodoItemDetailView(generics.RetrieveUpdateDestroyAPIView):  # type: ignore[misc]
    serializer_class = TodoItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        return TodoItem.objects.filter(
            todo_list__user=self.request.user,
        )

    def perform_update(self, serializer: TodoItemSerializer) -> None:
        if "is_completed" in self.request.data:
            is_completed = self.request.data["is_completed"]
            if is_completed and not serializer.instance.is_completed:
                serializer.save(completed_at=timezone.now())
            elif not is_completed and serializer.instance.is_completed:
                serializer.save(completed_at=None)
            else:
                serializer.save()
        else:
            serializer.save()


# todos/views.py
