from django.urls import path
from . import views

app_name='basic_app'

urlpatterns = [
    path('', views.basic_app, name='basic_app'),     
]