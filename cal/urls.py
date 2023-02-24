from django.contrib import admin
from django.urls import path
from .import views

app_name = 'cal'
urlpatterns = [
    path('index/', views.index, name='index'),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('event/new/', views.event, name='event_new'),
    path('event/edit/(?P<event_id>\d+)/', views.event, name='event_edit'),
    path('/showgc', views.CalendarView1.as_view(), name='sync'),
]
