from django.apps import AppConfig


class TodosConfig(AppConfig):  # type: ignore[misc]
    default_auto_field = "django.db.models.BigAutoField"
    name = "todos"


# todos/apps.py
