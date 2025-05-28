from django.db import models
from django.contrib.auth.models import User


class Banco(models.TextChoices):
    ITAU = 'Itau', 'itau'
    NUBANK = 'Nubank', 'nubank'
    BRADESCO = 'Bradesco', 'bradesco'
    CAIXA = 'Caixa', 'caixa'
    SANTANDER = 'Santander', 'santander'
    INTER = 'Inter', 'inter'

class Status(models.TextChoices):
    ATIVO = 'Ativo', 'ativo'
    INATIVO = 'Inativo', 'inativo'

class Tipos(models.TextChoices):
    ENTRADA = 'ENTRADA', 'entrada'
    SAIDA = 'SAIDA', 'saida'

class Categoria(models.TextChoices):
    SALARIO = 'Salario', 'salario'
    COMIDA = 'Comida', 'comida'
    LAZER = 'Lazer', 'lazer'
    ALUGUEL = 'Aluguel', 'aluguel'
    OUTROS = 'Outros', 'outros'

class Conta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contas')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    banco = models.CharField(max_length=50, choices=Banco.choices)
    status = models.CharField(max_length=50, choices=Status.choices)

    class Meta:
        unique_together = ('usuario', 'banco') # sem duplicar conta para o mesmo usuario

    def __str__(self):
        return f'{self.banco} - R${self.valor:.2f} - {self.usuario.username}'
    
class Historico(models.Model):
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='Historicos')
    tipo = models.CharField(max_length=10, choices=Tipos.choices, default=Tipos.ENTRADA)
    categoria = models.CharField(max_length=20, choices=Categoria.choices, default=Categoria.OUTROS)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.tipo} - {self.categoria} - R${self.valor:.2f} - {self.data}'
    