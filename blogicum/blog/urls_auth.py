from django.urls import path

from . import views_auth

app_name = 'auth'

urlpatterns = [
    path('', views_auth.RegistrationView.as_view(), name='registration'),
]
