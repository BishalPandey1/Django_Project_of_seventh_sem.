from django.urls import path
from . import views

app_name = "whiteboard"

urlpatterns = [
    path("",                       views.whiteboard_page,    name="whiteboard-page"),
    path("overlay/",               views.whiteboard_overlay, name="whiteboard-overlay"),
    path("annotate/",              views.whiteboard_annotate,name="whiteboard-annotate"),
    path("save/",                  views.whiteboard_save,    name="whiteboard-save"),
    path("load/<int:pk>/",         views.whiteboard_load,    name="whiteboard-load"),
    path("delete/<int:pk>/",       views.whiteboard_delete,  name="whiteboard-delete"),
]
