# responses/urls.py
from django.urls import path
from . import views

app_name = 'responses'

urlpatterns = [
    path('', views.UserResponsesView.as_view(), name='user_responses'),
    path('<int:pk>/accept/', views.accept_response, name='accept'),
    path('<int:pk>/delete/', views.delete_response, name='delete'),
]
