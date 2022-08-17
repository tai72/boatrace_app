from django.urls import path

from . import views


app_name = 'daily_result'
urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('daily-result-form/', views.DailyResultFormView.as_view(), name="daily_result_form"),
    path('daily-result', views.DailyResultView.as_view(), name="daily_result"),
]
