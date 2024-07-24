# registros/models.py

from django.db import models

class RegistroHorasExtras(models.Model):
    nome_funcionario = models.CharField(max_length=100)
    dias_uteis = models.IntegerField()
    dsr = models.CharField(max_length=10)
    he60_qtde = models.CharField(max_length=10)
    he80_qtde = models.CharField(max_length=10)
    he80_qtde_noturno = models.CharField(max_length=10)
    he100_qtde = models.CharField(max_length=10)

    def __str__(self):
        return self.nome_funcionario
