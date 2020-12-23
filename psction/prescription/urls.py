""" Module to define url routes """

from django.urls import path
from django.urls import include

app_name = 'prescription_app'
urlpatterns = [
    path('', include('prescription.api.urls', namespace='prescription_api')),
]
