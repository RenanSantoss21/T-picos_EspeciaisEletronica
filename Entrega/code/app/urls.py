from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProcessoViewSet,
    AmostraContinuaViewSet,
    AmostraAtributoViewSet,
    dashboardView,
    IndexView,
    JsonInputView,
)

router = DefaultRouter()

router.register(r'processos', ProcessoViewSet, basename='processo')
router.register(r'amostras-continuas', AmostraContinuaViewSet, basename='amostra-continua')
router.register(r'amostras-atributos', AmostraAtributoViewSet, basename='amostra-atributo')

urlpatterns = [
    path('api/', include(router.urls)),
    path('dashboard/<int:pk>/', dashboardView.as_view(), name='dashboard'),
    path('json-input/', JsonInputView.as_view(), name='json_input'),
    path('', IndexView.as_view(), name='index'),
]