from rest_framework import serializers
from .models import Processo, AmostraContinua, AmostraAtributo

class AmostraContinuaSerializer(serializers.ModelSerializer):
    # Expõe os cálculos das propriedades diretamente no JSON de resposta
    ponto_x = serializers.ReadOnlyField(source='media')
    ponto_r = serializers.ReadOnlyField(source='amplitude')
    ponto_mr = serializers.ReadOnlyField(source='amplitude_movel')

    class Meta:
        model = AmostraContinua
        fields = ['id', 'processo', 'valores', 'data_coleta', 'ponto_x', 'ponto_r', 'ponto_mr']

class AmostraAtributoSerializer(serializers.ModelSerializer):
    # Expõe a proporção para ser plotada nas cartas P ou U
    ponto_grafico = serializers.ReadOnlyField(source='proporcao')

    class Meta:
        model = AmostraAtributo
        fields = ['id', 'processo', 'tamanho_amostra', 'quantidade_ocorrencias', 'data_coleta', 'ponto_grafico']

class ProcessoSerializer(serializers.ModelSerializer):
    limites_controle = serializers.SerializerMethodField()
    amostras = serializers.SerializerMethodField()

    class Meta:
        model = Processo
        fields = ['id', 'nome', 'tipo_carta', 'criado_em', 'usar_regras_western', 'limites_controle', 'amostras']

    def get_limites_controle(self, obj):
        return obj.calcular_limites()

    def get_amostras(self, obj):
        if obj.tipo_carta in ['XR', 'IMR']:

            amostras = obj.amostras_continuas.all() 
            return AmostraContinuaSerializer(amostras, many=True).data
        else:
            amostras = obj.amostras_atributos.all()
            return AmostraAtributoSerializer(amostras, many=True).data