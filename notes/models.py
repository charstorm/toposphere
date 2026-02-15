from django.conf import settings
from django.db import models


class Note(models.Model):  # type: ignore[misc]
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return str(self.title)


# notes/models.py
