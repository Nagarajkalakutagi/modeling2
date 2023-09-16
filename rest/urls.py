from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

rout = DefaultRouter()
rout.register('show_result', ResultView, basename="show_result")
rout.register('add_users', AddUser, basename='add_users')

urlpatterns = [
    path('', include(rout.urls)),
]
