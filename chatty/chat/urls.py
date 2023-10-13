from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='first_page'),
    path('<str:room_name>/', views.room, name='room')
]
