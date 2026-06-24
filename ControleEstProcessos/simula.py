import requests
import random
import time

# Configure a URL base da sua API
BASE_URL = "http://127.0.0.1:8000/api"

# Se estiver usando Token, preencha aqui. Caso contrário, deixe vazio.
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Token 2c9e16fd4425e31be2d9bb6678e333bee6ea7bf7" 
}

def criar_processos():
    """Cria os 4 tipos de processos e retorna seus IDs."""
    processos_dados = [
        {"nome": "Diâmetro de Rolamentos (X-R)", "tipo_carta": "XR"},
        {"nome": "Pressão do Reator (I-MR)", "tipo_carta": "IMR"},
        {"nome": "Aprovação de Lotes (P)", "tipo_carta": "P"},
        {"nome": "Falhas de Solda por Placa (U)", "tipo_carta": "U"},
    ]
    
    ids = {}
    for proc in processos_dados:
        resposta = requests.post(f"{BASE_URL}/processos/", json=proc, headers=HEADERS)
        if resposta.status_code == 201:
            dados = resposta.json()
            ids[dados['tipo_carta']] = dados['id']
            print(f"[OK] Processo {dados['nome']} criado com ID {dados['id']}")
        else:
            print(f"[ERRO] Falha ao criar processo {proc['nome']}: {resposta.text}")
            
    return ids

def injetar_dados(ids):
    """Gera e envia dados estatísticos para cada processo criado."""
    qtd_amostras = 15
    print("\nIniciando injeção de amostras...")

    for i in range(qtd_amostras):
        # ---------------------------------------------------------
        # 1. Dados para Carta X-R (Média 50.0, Desvio 0.5, n=4)
        if 'XR' in ids:
            valores_xr = [round(random.gauss(50.0, 0.5), 2) for _ in range(4)]
            # Simulando um deslocamento (causa especial) nas últimas 3 amostras
            if i > 11: 
                valores_xr = [round(v + 1.2, 2) for v in valores_xr]
                
            requests.post(f"{BASE_URL}/amostras-continuas/", json={
                "processo": ids['XR'], "valores": valores_xr
            }, headers=HEADERS)

        # ---------------------------------------------------------
        # 2. Dados para Carta I-MR (Média 120.0, Desvio 2.0, n=1)
        if 'IMR' in ids:
            valor_imr = [round(random.gauss(120.0, 2.0), 2)]
            requests.post(f"{BASE_URL}/amostras-continuas/", json={
                "processo": ids['IMR'], "valores": valor_imr
            }, headers=HEADERS)

        # ---------------------------------------------------------
        # 3. Dados para Carta P (Lotes de 100 peças, ~4% de falha)
        if 'P' in ids:
            tamanho_lote = random.choice([95, 100, 105]) # Tamanho variável do lote
            # Simulando quantidade de defeituosos
            defeituosos = int(random.gauss(4, 1.5)) 
            defeituosos = max(0, defeituosos) # Evita números negativos
            
            requests.post(f"{BASE_URL}/amostras-atributos/", json={
                "processo": ids['P'], 
                "tamanho_amostra": tamanho_lote,
                "quantidade_ocorrencias": defeituosos
            }, headers=HEADERS)

        # ---------------------------------------------------------
        # 4. Dados para Carta U (5 unidades inspecionadas, ~2 defeitos/unidade)
        if 'U' in ids:
            unidades_inspecionadas = 5
            # Total de defeitos na amostra
            total_defeitos = int(random.gauss(10, 3)) 
            total_defeitos = max(0, total_defeitos)
            
            # Simulando um pico de anomalia na amostra 7
            if i == 7:
                total_defeitos = 28
                
            requests.post(f"{BASE_URL}/amostras-atributos/", json={
                "processo": ids['U'], 
                "tamanho_amostra": unidades_inspecionadas,
                "quantidade_ocorrencias": total_defeitos
            }, headers=HEADERS)

        print(f"Lote de amostras {i+1}/{qtd_amostras} enviado.")
        time.sleep(0.2) # Pausa rápida para não sobrecarregar o servidor local

if __name__ == "__main__":
    print("Verifique se o servidor Django (runserver) está rodando na porta 8000.")
    time.sleep(2)
    ids_processos = criar_processos()
    
    if ids_processos:
        injetar_dados(ids_processos)
        print("\n[CONCLUÍDO] Banco de dados populado com sucesso!")
        print("Acesse http://127.0.0.1:8000/ para ver o dashboard dinâmico.")