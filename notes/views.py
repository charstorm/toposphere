from typing import Any

from django.db import models
from rest_framework import generics, permissions

from .models import Note
from .serializers import NoteSerializer


class NoteListCreateView(generics.ListCreateAPIView):  # type: ignore[misc]
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        user = self.request.user
        queryset = Note.objects.filter(user=user)

        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) | models.Q(content__icontains=search)
            )
        return queryset

    def perform_create(self, serializer: NoteSerializer) -> None:
        serializer.save(user=self.request.user)


class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):  # type: ignore[misc]
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        return Note.objects.filter(user=self.request.user)


# notes/views.py
