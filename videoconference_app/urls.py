from django.urls import path
from . import views
from .views import save_recording

urlpatterns = [
    path('', views.index, name='index'),
    path('features/', views.features, name='features'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('meeting/', views.videocall, name='meeting'),
    path('join_room/', views.join_room, name='join_room'),
    path('random_call/', views.random_call, name='random_call'),
    path('save-recording/', save_recording, name='save_recording'),
]
