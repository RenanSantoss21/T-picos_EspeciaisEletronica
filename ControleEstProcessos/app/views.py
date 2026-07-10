from rest_framework import viewsets
from django.views.generic import TemplateView
from .models import AmostraAtributo, AmostraContinua, Processo, Configuracao
from .serializers import AmostraAtributoSerializer, AmostraContinuaSerializer, ProcessoSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View
import json

class ProcessoViewSet(viewsets.ModelViewSet):
    queryset = Processo.objects.all()
    serializer_class = ProcessoSerializer


class AmostraContinuaViewSet(viewsets.ModelViewSet):
    queryset = AmostraContinua.objects.all()
    serializer_class = AmostraContinuaSerializer


class AmostraAtributoViewSet(viewsets.ModelViewSet):
    queryset = AmostraAtributo.objects.all()
    serializer_class = AmostraAtributoSerializer


class dashboardView(TemplateView):
    template_name = 'app/dashboard.html'


class IndexView(TemplateView):
    template_name = 'app/index.html'


class JsonInputView(TemplateView):
    template_name = 'app/json_input.html'

@method_decorator(csrf_exempt, name='dispatch')
class ToggleLedsView(View):
    def get(self, request):
        config, created = Configuracao.objects.get_or_create(id=1)
        return JsonResponse({'leds_on': config.alertas_led_ligados})

    def post(self, request):
        config, created = Configuracao.objects.get_or_create(id=1)
        config.alertas_led_ligados = not config.alertas_led_ligados
        config.save()
        return JsonResponse({'leds_on': config.alertas_led_ligados})