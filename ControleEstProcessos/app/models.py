from django.db import models
from django.db.models import F, Avg
from .cartas import CartaU, CartaXR, CartaP, CartaIMR
import math


class Processo(models.Model):
    TIPO_CARTA_CHOICES = [
        ('XR', 'X-R'),
        ('IMR', 'I-MR'),
        ('P', 'P'),
        ('U', 'U')
    ]
    nome =models.CharField(max_length=100)
    tipo_carta = models.CharField(max_length=3, choices=TIPO_CARTA_CHOICES)
    criado_em = models.DateTimeField(auto_now_add=True)

    lse = models.FloatField(null=True, blank=True, help_text="Limite Superior de Especificação")
    lie = models.FloatField(null=True, blank=True, help_text="Limite Inferior de Especificação")
    usar_regras_western = models.BooleanField(default=False, help_text="Ativa a verificação das Regras do Western Electric Handbook")
    
    @property
    def estrategia_calculo(self):
        estrategias = {
            'XR': CartaXR(),
            'P': CartaP(),
            'IMR': CartaIMR(),
            'U': CartaU(),
        }
        return estrategias.get(self.tipo_carta)

    def calcular_limites(self):
        estrategia = self.estrategia_calculo
        
        if not estrategia:
            raise ValueError(f"Estratégia não implementada para {self.tipo_carta}")

        # Busca as amostras corretas baseadas no tipo de carta
        if self.tipo_carta in ['XR', 'IMR']:
            amostras = self.amostras_continuas.all()
        else:
            amostras = self.amostras_atributos.all()
            
        # Executa o polimorfismo
        return estrategia.calcular_limites(amostras, usar_regras_western=self.usar_regras_western)

class AmostraContinua(models.Model):
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='amostras_continuas')
    valores = models.JSONField(help_text="Lista de medições numéricas")
    data_coleta = models.DateTimeField(auto_now_add=True)

    @property
    def media(self):
        if not self.valores:
            return 0
        return sum(self.valores) / len(self.valores)
    
    @property
    def amplitude(self):
        if not self.valores or len(self.valores) < 2:
            return 0
        return max(self.valores) - min(self.valores)
    
    @property
    def amplitude_movel(self):
        if len(self.valores) != 1:
            return None
        
        amostra_anterior = AmostraContinua.objects.filter(
            processo=self.processo, 
            data_coleta__lt=self.data_coleta
        ).order_by('-data_coleta').first()

        if amostra_anterior and amostra_anterior.valores:
            return abs(self.valores[0] - amostra_anterior.valores[0])
        return 0
    

class AmostraAtributo(models.Model):
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='amostras_atributos')
    tamanho_amostra = models.PositiveIntegerField(help_text="Tamanho do lote/subgrupo (n)")
    quantidade_ocorrencias = models.PositiveIntegerField(help_text="Nº de itens defeituosos (P) ou total de defeitos (U)")
    data_coleta = models.DateTimeField(auto_now_add=True)

    @property
    def proporcao(self):
        if self.tamanho_amostra == 0:
            return 0
        return self.quantidade_ocorrencias / self.tamanho_amostra