from django.urls import path

from . import views


app_name = 'daily_result'
urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
]
