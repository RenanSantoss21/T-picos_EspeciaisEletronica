import json
import os
import math
from datetime import datetime, timedelta

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def processar_xr():
    raw_data = load_json('Docs/JSON_Base/dados1_modificados.json')
    amostras_dict = raw_data['Amostras']
    
    # n = 10 para todas as amostras
    A2 = 0.308
    D3 = 0
    D4 = 1.777
    
    amostras_processadas = []
    soma_x = 0
    soma_r = 0
    
    # Usaremos uma data base e incrementaremos 1 hora por amostra para simular a coleta
    data_base = datetime(2026, 6, 1, 8, 0, 0)
    
    for key, valores in amostras_dict.items():
        media = sum(valores) / len(valores)
        amplitude = max(valores) - min(valores)
        
        soma_x += media
        soma_r += amplitude
        
        amostras_processadas.append({
            "ponto_x": round(media, 4),
            "ponto_r": round(amplitude, 4),
            "data_coleta": (data_base + timedelta(hours=int(key))).isoformat()
        })
        
    k = len(amostras_dict)
    x_bar_bar = soma_x / k
    r_bar = soma_r / k
    
    lsc_x = x_bar_bar + A2 * r_bar
    lic_x = x_bar_bar - A2 * r_bar
    
    lsc_r = D4 * r_bar
    lic_r = D3 * r_bar
    
    payload = {
        "id": 1,
        "nome": "Dados XR (dados1.json)",
        "tipo_carta": "XR",
        "criado_em": datetime.now().isoformat(),
        "limites_controle": {
            "LC_X": round(x_bar_bar, 4),
            "LSC_X": round(lsc_x, 4),
            "LIC_X": round(lic_x, 4),
            "LC_R": round(r_bar, 4),
            "LSC_R": round(lsc_r, 4),
            "LIC_R": round(lic_r, 4)
        },
        "amostras": amostras_processadas
    }
    save_json(payload, 'Docs/JSON_Prontos/dashboard_xr.json')
    print("dashboard_xr.json gerado.")

def processar_imr():
    raw_data = load_json('Docs/JSON_Base/dados2_modificados.json')
    amostras_dict = raw_data.get('amostras', raw_data.get('Amostras'))
    
    amostras_processadas = []
    soma_x = 0
    amplitudes_moveis = []
    
    data_base = datetime(2026, 6, 1, 8, 0, 0)
    
    keys_ordenadas = sorted([int(k) for k in amostras_dict.keys()])
    valor_anterior = None
    
    for idx, key in enumerate(keys_ordenadas):
        valor = amostras_dict[str(key)][0]
        soma_x += valor
        
        mr = 0
        if valor_anterior is not None:
            mr = abs(valor - valor_anterior)
            amplitudes_moveis.append(mr)
            
        valor_anterior = valor
        
        amostras_processadas.append({
            "ponto_x": round(valor, 4),
            "ponto_mr": round(mr, 4) if idx > 0 else None,
            "data_coleta": (data_base + timedelta(hours=key)).isoformat()
        })
        
    k = len(amostras_dict)
    x_bar = soma_x / k
    mr_bar = sum(amplitudes_moveis) / len(amplitudes_moveis)
    
    lsc_i = x_bar + 3 * (mr_bar / 1.128)
    lic_i = x_bar - 3 * (mr_bar / 1.128)
    
    lsc_mr = 3.267 * mr_bar
    lic_mr = 0
    
    payload = {
        "id": 2,
        "nome": "Dados I-MR (dados2.json)",
        "tipo_carta": "IMR",
        "criado_em": datetime.now().isoformat(),
        "limites_controle": {
            "LC_I": round(x_bar, 4),
            "LSC_I": round(lsc_i, 4),
            "LIC_I": round(lic_i, 4),
            "LC_MR": round(mr_bar, 4),
            "LSC_MR": round(lsc_mr, 4),
            "LIC_MR": round(lic_mr, 4)
        },
        "amostras": amostras_processadas
    }
    save_json(payload, 'Docs/JSON_Prontos/dashboard_imr.json')
    print("dashboard_imr.json gerado.")

def processar_p():
    raw_data = load_json('Docs/JSON_Base/dados3_modificados.json')
    amostras_dict = raw_data['Amostras']
    
    amostras_processadas = []
    total_defeituosos = 0
    total_inspecionado = 0
    
    data_base = datetime(2026, 6, 1, 8, 0, 0)
    
    for key, valores in amostras_dict.items():
        n = len(valores) # 10
        defeituosos = sum(1 for x in valores if x < 49.00)
        
        total_defeituosos += defeituosos
        total_inspecionado += n
        
        proporcao = defeituosos / n
        
        amostras_processadas.append({
            "ponto_grafico": round(proporcao, 4),
            "data_coleta": (data_base + timedelta(hours=int(key))).isoformat()
        })
        
    p_bar = total_defeituosos / total_inspecionado
    n_medio = total_inspecionado / len(amostras_dict)
    
    desvio = math.sqrt((p_bar * (1 - p_bar)) / n_medio)
    
    lsc_p = p_bar + 3 * desvio
    lic_p = max(0, p_bar - 3 * desvio)
    
    payload = {
        "id": 3,
        "nome": "Dados P (dados3.json)",
        "tipo_carta": "P",
        "criado_em": datetime.now().isoformat(),
        "limites_controle": {
            "LC_P": round(p_bar, 4),
            "LSC_P": round(lsc_p, 4),
            "LIC_P": round(lic_p, 4)
        },
        "amostras": amostras_processadas
    }
    save_json(payload, 'Docs/JSON_Prontos/dashboard_p.json')
    print("dashboard_p.json gerado.")

if __name__ == "__main__":
    processar_xr()
    processar_imr()
    processar_p()
    print("Todos os dados foram processados com sucesso!")
