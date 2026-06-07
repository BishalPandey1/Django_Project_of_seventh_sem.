from django.urls import path
from . import views

app_name = "teacher"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("task/new/", views.task_create, name="task_create"),
    path("review/", views.review_submissions, name="review"),
    path("review/<int:sub_id>/grade/", views.grade_submission, name="grade"),
    path("toggle/<int:student_id>/<str:module_id>/", views.toggle_module_access, name="toggle_module"),
    path("admin/", views.admin_home, name="admin_home"),
    path("admin/<int:user_id>/role/", views.change_role, name="change_role"),
]
