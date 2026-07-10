import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Processo, AmostraContinua, AmostraAtributo, Configuracao
from .serializers import AmostraContinuaSerializer, AmostraAtributoSerializer

class TelemetriaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.buffer_temp = []
        self.buffer_hum = []
        await self.channel_layer.group_add("dashboard_updates", self.channel_name)
        await self.accept()
        print("Cliente WebSocket conectado via Channels.")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("dashboard_updates", self.channel_name)
        print("Cliente WebSocket desconectado.")

    async def receive(self, text_data):
        try:
            dados = json.loads(text_data)
            temp = dados.get("temperature")
            hum = dados.get("humidity")
            
            if temp is not None and hum is not None:
                # 1. Processamento Instantâneo (I-MR)
                resultado_imr = await self.processar_imr(temp, hum)
                
                # Responde à placa imediatamente com base no I-MR
                cmd = {"pattern": resultado_imr["pattern"], "leds_on": resultado_imr["leds_on"]}
                await self.send(text_data=json.dumps(cmd))
                
                # Broadcast do I-MR
                await self.channel_layer.group_send(
                    "dashboard_updates",
                    {
                        "type": "nova_amostra",
                        "processo_temp_id": resultado_imr["proc_temp_id"],
                        "processo_hum_id": resultado_imr["proc_hum_id"],
                        "amostra_temp": resultado_imr["amostra_temp"],
                        "amostra_hum": resultado_imr["amostra_hum"],
                        "limites_temp": resultado_imr["limites_temp"],
                        "limites_hum": resultado_imr["limites_hum"],
                    }
                )

                # 2. Processamento em Lote (X-R, P, U)
                self.buffer_temp.append(temp)
                self.buffer_hum.append(hum)
                
                if len(self.buffer_temp) >= 10:
                    resultado_lote = await self.processar_lote(self.buffer_temp, self.buffer_hum)
                    self.buffer_temp = []
                    self.buffer_hum = []
                    
                    # Faz o broadcast do lote
                    await self.channel_layer.group_send(
                        "dashboard_updates",
                        {
                            "type": "nova_amostra",
                            "processo_temp_id": resultado_lote["proc_temp_id"],
                            "processo_hum_id": resultado_lote["proc_hum_id"],
                            "proc_p_id": resultado_lote["proc_p_id"],
                            "proc_u_id": resultado_lote["proc_u_id"],
                            "amostra_temp": resultado_lote["amostra_temp"],
                            "amostra_hum": resultado_lote["amostra_hum"],
                            "amostra_p": resultado_lote["amostra_p"],
                            "amostra_u": resultado_lote["amostra_u"],
                            "limites_temp": resultado_lote["limites_temp"],
                            "limites_hum": resultado_lote["limites_hum"],
                            "limites_p": resultado_lote["limites_p"],
                            "limites_u": resultado_lote["limites_u"],
                        }
                    )
        except Exception as e:
            print(f"Erro no Consumer: {e}")

    async def nova_amostra(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def processar_imr(self, temperatura, umidade):
        proc_temp, _ = Processo.objects.get_or_create(
            nome="ESP32 Temperatura (I-MR)",
            defaults={'tipo_carta': 'IMR'}
        )
        proc_hum, _ = Processo.objects.get_or_create(
            nome="ESP32 Umidade (I-MR)",
            defaults={'tipo_carta': 'IMR'}
        )

        amostra_temp = AmostraContinua.objects.create(processo=proc_temp, valores=[temperatura])
        amostra_hum = AmostraContinua.objects.create(processo=proc_hum, valores=[umidade])

        config, _ = Configuracao.objects.get_or_create(id=1)
        leds_on = config.alertas_led_ligados

        limites_temp = proc_temp.calcular_limites()
        limites_hum = proc_hum.calcular_limites()

        pattern = "normal"
        temp_alert = None
        hum_alert = None

        if proc_temp.amostras_continuas.count() >= 15 and proc_hum.amostras_continuas.count() >= 15 and leds_on:
            if limites_temp and 'LSC_I' in limites_temp and 'LIC_I' in limites_temp:
                if temperatura > limites_temp['LSC_I']:
                    temp_alert = "upper_alert"
                elif temperatura < limites_temp['LIC_I']:
                    temp_alert = "lower_alert"

            if limites_hum and 'LSC_I' in limites_hum and 'LIC_I' in limites_hum:
                if umidade > limites_hum['LSC_I']:
                    hum_alert = "upper_alert"
                elif umidade < limites_hum['LIC_I']:
                    hum_alert = "lower_alert"

            if temp_alert and hum_alert:
                if temp_alert == hum_alert:
                    pattern = temp_alert 
                else:
                    pattern = "critical_mixed"
            elif temp_alert:
                pattern = temp_alert
            elif hum_alert:
                pattern = hum_alert
        
        return {
            "pattern": pattern,
            "leds_on": leds_on,
            "proc_temp_id": proc_temp.id,
            "proc_hum_id": proc_hum.id,
            "amostra_temp": AmostraContinuaSerializer(amostra_temp).data,
            "amostra_hum": AmostraContinuaSerializer(amostra_hum).data,
            "limites_temp": limites_temp,
            "limites_hum": limites_hum
        }

    @database_sync_to_async
    def processar_lote(self, temperaturas, umidades):
        proc_temp, _ = Processo.objects.get_or_create(
            nome="ESP32 Temperatura (X-R)",
            defaults={'tipo_carta': 'XR'}
        )
        proc_hum, _ = Processo.objects.get_or_create(
            nome="ESP32 Umidade (X-R)",
            defaults={'tipo_carta': 'XR'}
        )
        proc_p, _ = Processo.objects.get_or_create(
            nome="ESP32 Temperatura (P) - Defeitos >30°C",
            defaults={'tipo_carta': 'P'}
        )
        proc_u, _ = Processo.objects.get_or_create(
            nome="ESP32 Anomalias (U) - Temp/Hum",
            defaults={'tipo_carta': 'U'}
        )

        amostra_temp = AmostraContinua.objects.create(processo=proc_temp, valores=temperaturas)
        amostra_hum = AmostraContinua.objects.create(processo=proc_hum, valores=umidades)
        
        defeitos_temp = sum(1 for t in temperaturas if t > 30)
        defeitos_hum = sum(1 for h in umidades if h > 60)
        total_anomalias = defeitos_temp + defeitos_hum

        amostra_p = AmostraAtributo.objects.create(processo=proc_p, tamanho_amostra=10, quantidade_ocorrencias=defeitos_temp)
        amostra_u = AmostraAtributo.objects.create(processo=proc_u, tamanho_amostra=10, quantidade_ocorrencias=total_anomalias)

        return {
            "proc_temp_id": proc_temp.id,
            "proc_hum_id": proc_hum.id,
            "proc_p_id": proc_p.id,
            "proc_u_id": proc_u.id,
            "amostra_temp": AmostraContinuaSerializer(amostra_temp).data,
            "amostra_hum": AmostraContinuaSerializer(amostra_hum).data,
            "amostra_p": AmostraAtributoSerializer(amostra_p).data,
            "amostra_u": AmostraAtributoSerializer(amostra_u).data,
            "limites_temp": proc_temp.calcular_limites(),
            "limites_hum": proc_hum.calcular_limites(),
            "limites_p": proc_p.calcular_limites(),
            "limites_u": proc_u.calcular_limites()
        }
