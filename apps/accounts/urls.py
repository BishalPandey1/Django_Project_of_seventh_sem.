from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('home/', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('lessons/', views.lessons_view, name='lessons'),
    path('lessons/<str:lesson_title>/<str:topic_title>/', views.topic_detail_view, name='topic_detail'),
    path('help/', views.help_view, name='help'),
    path('logout/', views.logout_view, name='logout'),
]
