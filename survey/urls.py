from django.urls import path

from . import views

urlpatterns = [
    path('surveys/', views.surveys, name='surveys'),
    path('surveys/<int:survey_id>', views.survey, name='survey'),
    path('surveys/<int:survey_id>/<int:question_id>', views.survey_question, name='survey_question'),
    path('accounts/register/', views.register, name='register'),
    path('', views.index, name='index'),
]