from django.urls import path
from . import views

urlpatterns = [
    path('academic-setup/', views.academic_setup, name='academic_setup'),
]