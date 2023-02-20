from django.urls import path

from . import views


app_name = 'daily_result'
urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('daily-result-form/', views.DailyResultFormView.as_view(), name="daily_result_form"), 
    path('daily-result', views.DailyResultView.as_view(), name="daily_result"), 
    path('prob-form', views.ProbFormView.as_view(), name="prob_form"), 
    path('prob', views.ProbView.as_view(), name="prob"), 
    path('race-result-select/', views.RaceResultSelectView.as_view(), name="race_result_select"), 
    path('race-result/<str:race_date>/<str:place_id>/<str:race_no>/', views.RaceResultView.as_view(), name="race_result"), 
    path('inquiry/', views.InquiryView.as_view(), name="inquiry"), 
    path('current-situation', views.CurrentSituationView.as_view(), name="current_situation"), 
]
