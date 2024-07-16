# core/home/urls.py

from django.urls import path
from .views import home_view, speak_view  # Adjusted import

urlpatterns = [
    path('', home_view, name='home'),  # Ensure 'home_view' is correctly referenced
    path('speak/', speak_view, name='speak'),
    # Add more paths as needed
]
