from rest_framework import serializers

from .models import TodoItem, TodoList


class TodoItemSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = TodoItem
        fields = [
            "id",
            "title",
            "description",
            "is_completed",
            "created_at",
            "updated_at",
            "completed_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "completed_at"]


class TodoListSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    items = TodoItemSerializer(many=True, read_only=True)

    class Meta:
        model = TodoList
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# todos/serializers.py
