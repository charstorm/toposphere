from django.urls import path

from .views import (
    TodoItemDetailView,
    TodoItemListCreateView,
    TodoListDetailView,
    TodoListListCreateView,
)

urlpatterns = [
    path("todos/", TodoListListCreateView.as_view(), name="todo-list-create"),
    path("todos/<int:pk>/", TodoListDetailView.as_view(), name="todo-detail"),
    path(
        "todos/<int:list_id>/items/",
        TodoItemListCreateView.as_view(),
        name="todo-item-list-create",
    ),
    path(
        "todos/items/<int:pk>/",
        TodoItemDetailView.as_view(),
        name="todo-item-detail",
    ),
]

# todos/urls.py
