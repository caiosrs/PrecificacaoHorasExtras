# registros/urls.py

from django.urls import path
from .views import registro_horas_extras, sucesso

urlpatterns = [
    path('', registro_horas_extras, name='registro_horas_extras'),
    path('sucesso/', sucesso, name='sucesso'),
]