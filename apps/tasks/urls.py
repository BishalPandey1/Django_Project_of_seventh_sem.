from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.list_tasks, name="list"),
    path("<int:task_id>/submit/", views.submit, name="submit"),
]
