from django.urls import path

from . import views


app_name = "explorer"


urlpatterns = [
    path("", views.modules_index, name="index"),
    path("linear/",     views.linear_view,     name="linear"),
    path("quadratic/",  views.quadratic_view,  name="quadratic"),
    path("trig/",       views.trig_view,       name="trig"),
    path("derivative/", views.derivative_view, name="derivative"),
    path("integral/",   views.integral_view,   name="integral"),
    path("geometry/",   views.geometry_view,   name="geometry"),
    path("transform/",  views.transform_view,  name="transform"),
    # HTMX update endpoints
    path("linear/update/",     views.linear_update,     name="linear_update"),
    path("quadratic/update/",  views.quadratic_update,  name="quadratic_update"),
    path("trig/update/",       views.trig_update,       name="trig_update"),
    path("derivative/update/", views.derivative_update, name="derivative_update"),
    path("integral/update/",   views.integral_update,   name="integral_update"),
    path("geometry/update/",   views.geometry_update,   name="geometry_update"),
    path("transform/update/",  views.transform_update,  name="transform_update"),
    # Snapshot / compare endpoints (same body fragment as the update URL).
    path("linear/snapshot/",     views.linear_snapshot,     name="linear_snapshot"),
    path("quadratic/snapshot/",  views.quadratic_snapshot,  name="quadratic_snapshot"),
    path("trig/snapshot/",       views.trig_snapshot,       name="trig_snapshot"),
    path("derivative/snapshot/", views.derivative_snapshot, name="derivative_snapshot"),
    path("integral/snapshot/",   views.integral_snapshot,   name="integral_snapshot"),
    path("geometry/snapshot/",   views.geometry_snapshot,   name="geometry_snapshot"),
    path("transform/snapshot/",  views.transform_snapshot,  name="transform_snapshot"),
    path("statistics/",          views.statistics_view,     name="statistics"),
    path("statistics/update/",   views.statistics_update,   name="statistics_update"),
    path("statistics/snapshot/", views.statistics_snapshot, name="statistics_snapshot"),
    # Module-annotation routes (frozen-diagram whiteboard). One set per module
    # so the URL path is informative and the save endpoint can be reused by
    # the existing whiteboard.js whiteboard.save() consumer.
    path("<str:module>/annotations/",                views.annotation_list,   name="annotation_list"),
    path("<str:module>/annotations/save/",           views.annotation_save,   name="annotation_save"),
    path("<str:module>/annotations/load/<int:pk>/",  views.annotation_load,   name="annotation_load"),
    path("<str:module>/annotations/delete/<int:pk>/",views.annotation_delete, name="annotation_delete"),
]
