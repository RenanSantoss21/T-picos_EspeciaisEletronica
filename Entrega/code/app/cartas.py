from abc import ABC, abstractmethod
from .const import CONSTANTES_CEP
import math


class EstrategiaCarta(ABC):
    @abstractmethod
    def calcular_limites(self, amostras, usar_regras_western=False):
        pass

    def _calcular_zonas_western(self, limites, key_lsc, key_lc, prefix):
        sigma = (limites[key_lsc] - limites[key_lc]) / 3
        limites['Sigma'] = sigma
        limites[f'LSC_{prefix}_1S'] = limites[key_lc] + sigma
        limites[f'LIC_{prefix}_1S'] = limites[key_lc] - sigma
        limites[f'LSC_{prefix}_2S'] = limites[key_lc] + 2 * sigma
        limites[f'LIC_{prefix}_2S'] = limites[key_lc] - 2 * sigma

    def _avaliar_regras_western(self, amostras, lc, sigma):
        alertas = []
        valores = [getattr(a, 'media', getattr(a, 'proporcao', 0)) for a in amostras]
        
        for i, val in enumerate(valores):
            amostra_index = i + 1
            
            if val > lc + 3 * sigma or val < lc - 3 * sigma:
                alertas.append({"amostra_index": amostra_index, "regra": 1, "mensagem": "Ponto além de 3σ"})
            
            if i >= 2:
                janela = valores[i-2:i+1]
                acima = sum(1 for v in janela if v > lc + 2 * sigma)
                abaixo = sum(1 for v in janela if v < lc - 2 * sigma)
                if acima >= 2 or abaixo >= 2:
                    alertas.append({"amostra_index": amostra_index, "regra": 2, "mensagem": "2 de 3 pontos além de 2σ"})
            
            if i >= 4:
                janela = valores[i-4:i+1]
                acima = sum(1 for v in janela if v > lc + sigma)
                abaixo = sum(1 for v in janela if v < lc - sigma)
                if acima >= 4 or abaixo >= 4:
                    alertas.append({"amostra_index": amostra_index, "regra": 3, "mensagem": "4 de 5 pontos além de 1σ"})
            
            if i >= 7:
                janela = valores[i-7:i+1]
                acima = sum(1 for v in janela if v > lc)
                abaixo = sum(1 for v in janela if v < lc)
                if acima == 8 or abaixo == 8:
                    alertas.append({"amostra_index": amostra_index, "regra": 4, "mensagem": "8 pontos consecutivos do mesmo lado da média"})
                    
        return alertas

    def gerar_alertas(self, amostras, lsc, lic, tipo_carta):
        alertas = []
        for amostra in amostras:
            # Em cartas P ou U, acessamos 'proporcao'. Em X-R, seria 'media' ou 'amplitude'
            valor_ponto = getattr(amostra, 'proporcao', None) or getattr(amostra, 'media', 0)
            
            if valor_ponto > lsc:
                if tipo_carta in ['R', 'MR', 'U', 'P']:
                    alertas.append({
                        "amostra_id": amostra.id,
                        "tipo": "MANUTENÇÃO",
                        "mensagem": f"Variabilidade/Defeitos acima do limite (Ponto: {valor_ponto:.3f})."
                    })
                elif tipo_carta in ['X', 'I']:
                    alertas.append({
                        "amostra_id": amostra.id,
                        "tipo": "CALIBRAÇÃO",
                        "mensagem": f"Média deslocada para cima (Ponto: {valor_ponto:.3f})."
                    })
            
            elif valor_ponto < lic:
                if tipo_carta in ['X', 'I']:
                    alertas.append({
                        "amostra_id": amostra.id,
                        "tipo": "CALIBRAÇÃO",
                        "mensagem": f"Média deslocada para baixo (Ponto: {valor_ponto:.3f})."
                    })
        return alertas

    def calcular_capacidade(self, processo, media_global, desvio_estimado):

        if processo.lse is not None and processo.lie is not None:
            if desvio_estimado == 0:
                return {"erro": "Desvio estimado é zero. Processo sem variação."}
                
            cp = (processo.lse - processo.lie) / (6 * desvio_estimado)
            cpk_sup = (processo.lse - media_global) / (3 * desvio_estimado)
            cpk_inf = (media_global - processo.lie) / (3 * desvio_estimado)
            cpk = min(cpk_sup, cpk_inf)
            
            return {
                "Cp": round(cp, 2),
                "Cpk": round(cpk, 2),
                "status": "Capaz" if cpk >= 1 else "Incapaz"
            }
        
        return {
            "status": "Aguardando limites de engenharia (LSE/LIE)",
            "Cp": None,
            "Cpk": None
        }

class CartaXR(EstrategiaCarta):
    def calcular_limites(self, amostras, usar_regras_western=False):
        if not amostras: return {}

        n = len(amostras[0].valores)
        const = CONSTANTES_CEP.get(n, CONSTANTES_CEP[2])

        media_das_medias = sum(a.media for a in amostras) / amostras.count()
        media_das_amplitudes = sum(a.amplitude for a in amostras) / amostras.count()

        limites = {
            'LC_X': media_das_medias,
            'LSC_X': media_das_medias + (const['A2'] * media_das_amplitudes),
            'LIC_X': media_das_medias - (const['A2'] * media_das_amplitudes),
            'LC_R': media_das_amplitudes,
            'LSC_R': const['D4'] * media_das_amplitudes,
            'LIC_R': const['D3'] * media_das_amplitudes,
        }
        
        if usar_regras_western:
            self._calcular_zonas_western(limites, 'LSC_X', 'LC_X', 'X')
            limites['alertas_avancados'] = self._avaliar_regras_western(amostras, limites['LC_X'], limites['Sigma'])
            
        return limites


class CartaP(EstrategiaCarta):
    def calcular_limites(self, amostras, usar_regras_western=False):
        if not amostras: return {}

        total_defeituosos = sum(a.quantidade_ocorrencias for a in amostras)
        total_inspecionado = sum(a.tamanho_amostra for a in amostras)
    
        if total_inspecionado == 0: return {}

        p_bar = total_defeituosos / total_inspecionado
        n_medio = total_inspecionado / amostras.count()
        
        desvio_padrao = math.sqrt((p_bar * (1 - p_bar)) / n_medio)
        
        return {
            'LC_P': p_bar,
            'LSC_P': min(1, p_bar + 3 * desvio_padrao),
            'LIC_P': max(0, p_bar - 3 * desvio_padrao),
        }
    

class CartaIMR(EstrategiaCarta):
    def calcular_limites(self, amostras, usar_regras_western=False):
        if not amostras: return {}
        media_x = sum(a.media for a in amostras) / amostras.count()
        amplitudes_m_list = [a.amplitude_movel for a in amostras if a.amplitude_movel is not None]
        mr_bar = sum(amplitudes_m_list) / len(amplitudes_m_list)
        
        n = len(amostras[0].valores)
        const = CONSTANTES_CEP.get(n, CONSTANTES_CEP[2])
        # Constante para n=2 na amplitude móvel é 2.66 (3 / d2)
        limites = {
            'LC_I': media_x,
            'LSC_I': media_x + const['A2'] * mr_bar,
            'LIC_I': media_x - const['A2'] * mr_bar,
            'LC_MR': mr_bar,
            'LSC_MR': const['D4'] * mr_bar,
            'LIC_MR': const['D3'] * mr_bar,
        }
        
        if usar_regras_western:
            self._calcular_zonas_western(limites, 'LSC_I', 'LC_I', 'I')
            limites['alertas_avancados'] = self._avaliar_regras_western(amostras, limites['LC_I'], limites['Sigma'])
            
        return limites


class CartaU(EstrategiaCarta):
    def calcular_limites(self, amostras, usar_regras_western=False):
        if not amostras: return {}
        
        total_defeitos = sum(a.quantidade_ocorrencias for a in amostras)
        total_inspecionado = sum(a.tamanho_amostra for a in amostras)
        
        if total_inspecionado == 0: return {}
        
        # Média global de defeitos por unidade
        u_bar = total_defeitos / total_inspecionado
        # Tamanho médio da amostra (n)
        n_medio = total_inspecionado / len(amostras)
        
        # Função de desvio (Distribuição de Poisson)
        desvio_padrao = math.sqrt(u_bar / n_medio)
        
        lsc_u = u_bar + 3 * desvio_padrao
        lic_u = max(0, u_bar - 3 * desvio_padrao) # Limite não pode ser negativo
        
        alertas = self.gerar_alertas(amostras, lsc_u, lic_u, tipo_carta='U')

        return {
            'LC_U': round(u_bar, 4),
            'LSC_U': round(lsc_u, 4),
            'LIC_U': round(lic_u, 4),
            'Desvio_Padrao_Poisson': round(desvio_padrao, 4),
            'Alertas': alertas
        }
