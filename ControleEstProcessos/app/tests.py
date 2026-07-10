from django.test import TestCase
from app.models import Processo
from app.serializers import ProcessoSerializer

class TestWesternElectricAPI(TestCase):
    def test_processo_aceita_flag_western(self):
        # Testa se o model aceita o salvamento com a flag
        processo = Processo.objects.create(
            nome="Teste Western",
            tipo_carta="XR",
            usar_regras_western=True
        )
        self.assertTrue(processo.usar_regras_western)

    def test_serializer_expoe_flag_western(self):
        # Testa se a API expõe ou aceita a flag na serialização
        processo = Processo.objects.create(
            nome="Teste Western Serializer",
            tipo_carta="IMR",
            usar_regras_western=True
        )
        serializer = ProcessoSerializer(processo)
        self.assertIn('usar_regras_western', serializer.data)
        self.assertTrue(serializer.data['usar_regras_western'])

class TestCartasWestern(TestCase):
    def setUp(self):
        self.processo_xr = Processo.objects.create(
            nome="Proc XR", tipo_carta="XR", usar_regras_western=True
        )
        self.processo_imr = Processo.objects.create(
            nome="Proc IMR", tipo_carta="IMR", usar_regras_western=True
        )

    def test_carta_xr_calcula_zonas(self):
        # Simulando amostras mockadas. Como CartaXR calcula a partir de objetos reais:
        from app.models import AmostraContinua
        AmostraContinua.objects.create(processo=self.processo_xr, valores=[10, 12, 11])
        AmostraContinua.objects.create(processo=self.processo_xr, valores=[9, 11, 10])
        
        limites = self.processo_xr.calcular_limites()
        
        # Testando se as chaves das zonas estão presentes
        self.assertIn('Sigma', limites)
        self.assertIn('LSC_X_1S', limites)
        self.assertIn('LSC_X_2S', limites)
        self.assertIn('LIC_X_1S', limites)
        self.assertIn('LIC_X_2S', limites)
        
        # LSC = LC + 3Sigma -> Sigma = (LSC - LC) / 3
        # LSC_X_1S = LC + 1Sigma
        sigma_esperado = (limites['LSC_X'] - limites['LC_X']) / 3
        self.assertAlmostEqual(limites['Sigma'], sigma_esperado, places=3)
        self.assertAlmostEqual(limites['LSC_X_1S'], limites['LC_X'] + sigma_esperado, places=3)

    def test_sem_regras_western_nao_calcula_zonas(self):
        self.processo_xr.usar_regras_western = False
        self.processo_xr.save()
        from app.models import AmostraContinua
        AmostraContinua.objects.create(processo=self.processo_xr, valores=[10, 12, 11])
        limites = self.processo_xr.calcular_limites()
        self.assertNotIn('Sigma', limites)

class TestMotorAlertasWestern(TestCase):
    def setUp(self):
        self.processo_xr = Processo.objects.create(
            nome="Proc Motor", tipo_carta="XR", usar_regras_western=True
        )

    def _criar_amostras(self, medias):
        from app.models import AmostraContinua
        for idx, m in enumerate(medias):
            AmostraContinua.objects.create(processo=self.processo_xr, valores=[m, m, m])

    def test_regra1_ponto_alem_3sigma(self):
        # lc = 10, sigma = 1 (simulado simplificado)
        # Amostras com médias normais e um outlier na regra 1 ( > 3sigma )
        # Para forçar média = 10 e sigma ser consistente, usamos amplitudes 0 (MR=0/R=0) e manipulamos apenas a avaliação isolada se possível.
        # Na CartaXR, LC_X é a média das médias.
        # Vamos testar o método _avaliar_regras_western diretamente na classe base.
        from app.cartas import CartaXR
        from types import SimpleNamespace
        
        carta = CartaXR()
        # Mock de amostras contendo apenas o atributo `media`
        amostras = [SimpleNamespace(media=10, id=i) for i in range(1, 10)]
        # Injetar uma anomalia na amostra 5 (índice 4)
        amostras[4].media = 14 # 10 + 4sigma (sigma=1)
        
        # Testando diretamente o método que será implementado
        alertas = carta._avaliar_regras_western(amostras, lc=10, sigma=1)
        
        self.assertTrue(any(a['regra'] == 1 and a['amostra_index'] == 5 for a in alertas))

    def test_regra2_2_de_3_alem_2sigma(self):
        from app.cartas import CartaXR
        from types import SimpleNamespace
        carta = CartaXR()
        amostras = [SimpleNamespace(media=10, id=i) for i in range(1, 10)]
        # Regra 2: 2 de 3 pontos consecutivos > LC + 2sigma ou < LC - 2sigma
        amostras[2].media = 12.5 # > 10 + 2 (sigma=1)
        amostras[3].media = 10.5 # normal
        amostras[4].media = 12.1 # > 10 + 2 (sigma=1) -> Aqui dispara a regra (2 de 3)
        
        alertas = carta._avaliar_regras_western(amostras, lc=10, sigma=1)
        self.assertTrue(any(a['regra'] == 2 and a['amostra_index'] == 5 for a in alertas))

    def test_regra3_4_de_5_alem_1sigma(self):
        from app.cartas import CartaXR
        from types import SimpleNamespace
        carta = CartaXR()
        amostras = [SimpleNamespace(media=10, id=i) for i in range(1, 10)]
        # Regra 3: 4 de 5 consecutivos > LC + 1sigma ou < LC - 1sigma
        amostras[2].media = 11.2 # > 10 + 1 (sigma=1)
        amostras[3].media = 11.5 # > 10 + 1
        amostras[4].media = 10.5 # normal
        amostras[5].media = 11.1 # > 10 + 1
        amostras[6].media = 11.3 # > 10 + 1 -> dispara a regra (4 de 5)
        
        alertas = carta._avaliar_regras_western(amostras, lc=10, sigma=1)
        self.assertTrue(any(a['regra'] == 3 and a['amostra_index'] == 7 for a in alertas))

    def test_regra4_8_pontos_consecutivos_mesmo_lado(self):
        from app.cartas import CartaXR
        from types import SimpleNamespace
        carta = CartaXR()
        amostras = [SimpleNamespace(media=10, id=i) for i in range(1, 12)]
        # Regra 4: 8 consecutivos do mesmo lado do LC
        for i in range(2, 10):
            amostras[i].media = 10.2 # > LC (10)
        
        alertas = carta._avaliar_regras_western(amostras, lc=10, sigma=1)
        self.assertTrue(any(a['regra'] == 4 and a['amostra_index'] == 10 for a in alertas))

import pytest
from channels.testing import WebsocketCommunicator
from cartaControle.asgi import application
from app.models import Configuracao

@pytest.mark.asyncio
@pytest.mark.django_db
class TestDashboardWebsockets:
    async def test_telemetria_broadcasts_to_group(self):
        # 1. Configura um websocket "frontend" que apenas escuta
        communicator = WebsocketCommunicator(application, "/ws/telemetria/")
        connected, subprotocol = await communicator.connect()
        assert connected

        # 2. Configura um mock de ESP32 que envia dados
        esp32_communicator = WebsocketCommunicator(application, "/ws/telemetria/")
        connected_esp, _ = await esp32_communicator.connect()
        assert connected_esp

        # 3. O ESP32 envia telemetria
        await esp32_communicator.send_json_to({
            "temperature": 25.0,
            "humidity": 50.0
        })

        # O ESP32 deve receber uma resposta com pattern
        esp32_response = await esp32_communicator.receive_json_from()
        assert "pattern" in esp32_response

        # 4. O Frontend DEVE ter recebido um broadcast no grupo
        # Isso vai FALHAR na fase RED, pois ainda não configuramos o group_send!
        frontend_response = await communicator.receive_json_from()
        assert frontend_response["type"] == "nova_amostra"

        await communicator.disconnect()
        await esp32_communicator.disconnect()
