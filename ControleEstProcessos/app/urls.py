from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProcessoViewSet,
    AmostraContinuaViewSet,
    AmostraAtributoViewSet,
    dashboardView,
    IndexView,
    JsonInputView,
    ToggleLedsView,
)

router = DefaultRouter()

router.register(r'processos', ProcessoViewSet, basename='processo')
router.register(r'amostras-continuas', AmostraContinuaViewSet, basename='amostra-continua')
router.register(r'amostras-atributos', AmostraAtributoViewSet, basename='amostra-atributo')

urlpatterns = [
    path('api/', include(router.urls)),
    path('dashboard/<int:pk>/', dashboardView.as_view(), name='dashboard'),
    path('json-input/', JsonInputView.as_view(), name='json_input'),
    path('api/toggle-leds/', ToggleLedsView.as_view(), name='toggle_leds'),
    path('', IndexView.as_view(), name='index'),
]