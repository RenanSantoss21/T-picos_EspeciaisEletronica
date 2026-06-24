from rest_framework import viewsets
from django.views.generic import TemplateView
from .models import AmostraAtributo, AmostraContinua, Processo
from .serializers import AmostraAtributoSerializer, AmostraContinuaSerializer, ProcessoSerializer

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