# registros/urls.py

from django.urls import path
from .views import registro_horas_extras, sucesso, get_salario  # Importe get_salario aqui

urlpatterns = [
    path('', registro_horas_extras, name='registro_horas_extras'),
    path('registro_horas_extras/', registro_horas_extras, name='registro_horas_extras'),
    path('sucesso/', sucesso, name='sucesso'),
    path('get_salario/', get_salario, name='get_salario'),  # Rota para buscar o salário
    path('sucesso/', sucesso, name='sucesso'),
]