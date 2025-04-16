import math
import heapq 
import json
import time 

# --- Funções Auxiliares (Sem alterações) ---

def calcular_distancia_euclidiana(coords_cidade1, coords_cidade2):
    return math.dist(coords_cidade1, coords_cidade2)

def carregar_dados_cidades(caminho_arquivo_json):
    try:
        with open(caminho_arquivo_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        cidades = {
            item['city']: {
                'coords': (item['latitude'], item['longitude']),
                'population': item['population']
            }
            for item in dados
        }
        return cidades
    except FileNotFoundError:
        print(f"Erro: Arquivo JSON não encontrado em {caminho_arquivo_json}")
        return None
    except Exception as e:
        print(f"Erro ao carregar ou processar o JSON: {e}")
        return None

def construir_grafo(dados_cidades, r):
    grafo = {cidade: [] for cidade in dados_cidades}
    nomes_cidades = list(dados_cidades.keys())
    for i in range(len(nomes_cidades)):
        for j in range(i + 1, len(nomes_cidades)):
            nome_cidade1 = nomes_cidades[i]
            nome_cidade2 = nomes_cidades[j]
            dados_cidade1 = dados_cidades[nome_cidade1]
            dados_cidade2 = dados_cidades[nome_cidade2]
            distancia = calcular_distancia_euclidiana(dados_cidade1['coords'], dados_cidade2['coords'])
            if distancia <= r:
                grafo[nome_cidade1].append((nome_cidade2, distancia))
                grafo[nome_cidade2].append((nome_cidade1, distancia))
    return grafo

# --- Busca de Custo Uniforme (UCS) ---

def busca_custo_uniforme(grafo, dados_cidades, no_inicial, no_final):
    """
    Executa a Busca de Custo Uniforme (UCS)
    e imprime um resumo final detalhado no console.

    Args:
        grafo (dict): Representação da lista de adjacências.
        dados_cidades (dict): Dados das cidades incluindo população.
        no_inicial (str): Nome da cidade inicial.
        no_final (str): Nome da cidade de destino.

    Returns:
        tuple: (caminho, custo, estatisticas)
    """
    print(f"\n--- Iniciando Busca de Custo Uniforme (UCS): {no_inicial} -> {no_final} ---")
    inicio_tempo = time.time()

    # Dicionário para guardar estatísticas da busca
    estatisticas = {
        "total_expansoes": 0, 
        "custo_final": float('inf'),
        "caminho": None, 
        "caminho_detalhado": "", # String do caminho com distâncias
        "tempo_execucao": 0,
        "status": "Não Iniciado" 
    }

    # Caso base: nó inicial é o mesmo que o final
    if no_inicial == no_final:
        print("Nó inicial é o mesmo que o nó final.")
        estatisticas.update({"status": "Inicial igual ao Final", "caminho": [no_inicial], "custo_final": 0, "tempo_execucao": time.time() - inicio_tempo, "caminho_detalhado": no_inicial})
        return [no_inicial], 0, estatisticas
        
    # Verifica se os nós existem no grafo
    # (Nota: UCS pode encontrar um caminho mesmo que o nó final não tenha saídas, 
    # mas ambos devem existir como possíveis estados/chaves no dicionário de dados)
    if no_inicial not in dados_cidades or no_final not in dados_cidades:
         print(f"Erro: Nó inicial '{no_inicial}' ou Nó final '{no_final}' não encontrado nos dados das cidades.")
         estatisticas.update({"status": "Nó Inicial ou Final não existe", "tempo_execucao": time.time() - inicio_tempo})
         return None, float('inf'), estatisticas
        
    # --- Inicialização UCS ---
    # Fila de prioridade: armazena (custo_acumulado, populacao_atual, no_atual, caminho_ate_aqui)
    # Populacao é usada como critério de desempate secundário (menor população primeiro se custos iguais)
    fila_prio = [(0, dados_cidades[no_inicial]['population'], no_inicial, [no_inicial])] 
    
    # Conjunto de nós já visitados (expandidos) para evitar ciclos e redundância. 
    # Guarda o nó cujo caminho ótimo já foi encontrado e processado.
    visitados = set() 

    # --- Loop Principal da Busca UCS ---
    while fila_prio:
        # Retira o nó com o MENOR custo acumulado da fila
        custo_atual, _, no_atual, caminho_atual = heapq.heappop(fila_prio)

        # Se já visitamos (processamos) este nó, pulamos (já encontramos o caminho ótimo para ele)
        if no_atual in visitados:
            continue

        # Marca o nó atual como visitado (seu caminho ótimo foi encontrado agora)
        visitados.add(no_atual)
        estatisticas["total_expansoes"] += 1 # Conta como uma expansão válida
        
        # Imprime a expansão (moderado)
        print(f"  [{estatisticas['total_expansoes']:<4} UCS] Expandir: {no_atual:<15} (Custo Acum.: {custo_atual:.2f})")

        # --- Teste de Objetivo ---
        if no_atual == no_final:
            fim_tempo = time.time()
            estatisticas["tempo_execucao"] = fim_tempo - inicio_tempo
            estatisticas["custo_final"] = custo_atual
            estatisticas["caminho"] = caminho_atual
            estatisticas["status"] = "Caminho ótimo encontrado"

            # --- Formata Caminho com Distâncias ---
            partes_caminho_str = [caminho_atual[0]]
            for i in range(len(caminho_atual) - 1):
                cid_atual = caminho_atual[i]
                prox_cid = caminho_atual[i+1]
                dist_seg = None
                if cid_atual in grafo:
                     adj = grafo[cid_atual]
                     dist_tup = next((item for item in adj if item[0] == prox_cid), None)
                     if dist_tup: dist_seg = dist_tup[1]
                if dist_seg is not None:
                     partes_caminho_str.append(f"-> {prox_cid} (Dist: {dist_seg:.2f})")
                else:
                     partes_caminho_str.append(f"-> {prox_cid} (Dist: ??)")
            estatisticas["caminho_detalhado"] = " ".join(partes_caminho_str)
            # --- Fim Formatação ---

            # --- Imprime Resumo Final no Console ---
            print("\n--- Busca Finalizada ---")
            print(f"Total de Expansões de Nós: {estatisticas['total_expansoes']}") 
            print(f"Tempo de Execução: {estatisticas['tempo_execucao']:.4f} segundos") 
            print(f"Custo final calculado: {estatisticas['custo_final']:.2f}")
            
            print(f"\n--- Resultado Final ---")
            print(f"  Status: {estatisticas['status']}")
            print(f"  Caminho Encontrado ({len(caminho_atual)} cidades):")
            print(f"    {estatisticas['caminho_detalhado']}") 
            print(f"  Distância Total: {estatisticas['custo_final']:.2f}")
            print(f"  Total de Expansões de Nós: {estatisticas['total_expansoes']}")
            print(f"  Tempo de Execução: {estatisticas['tempo_execucao']:.4f} segundos")
            # --- Fim Impressão Console ---

            return caminho_atual, custo_atual, estatisticas

        # --- Expande Vizinhos ---
        # Se não é o nó final, adiciona seus vizinhos à fila
        for vizinho, distancia in grafo.get(no_atual, []):
            # Apenas considera vizinhos que ainda NÃO foram visitados (expandidos)
            if vizinho not in visitados:
                novo_custo = custo_atual + distancia
                novo_caminho = list(caminho_atual) # Copia o caminho atual
                novo_caminho.append(vizinho)
                # Adiciona o vizinho na fila com seu novo custo e caminho
                heapq.heappush(fila_prio, (novo_custo, dados_cidades[vizinho]['population'], vizinho, novo_caminho))

    # --- Fim do Loop: Fila Vazia ---
    # Se a fila esvaziar antes de encontrar o objetivo, não há caminho
    fim_tempo = time.time()
    estatisticas["tempo_execucao"] = fim_tempo - inicio_tempo
    estatisticas["status"] = "Nenhum caminho encontrado (Espaço de busca esgotado)"
    
    # --- Imprime Resumo Final (Sem Caminho) ---
    print("\n--- Busca Finalizada ---")
    print(f"Total de Expansões de Nós: {estatisticas['total_expansoes']}") 
    print(f"Tempo de Execução: {estatisticas['tempo_execucao']:.4f} segundos") 
    print(f"Nenhum caminho encontrado entre {no_inicial} e {no_final}.")
    print(f"\n--- Resultado Final ---")
    print(f"  Status: {estatisticas['status']}")
    print(f"  Total de Expansões de Nós: {estatisticas['total_expansoes']}")
    print(f"  Tempo de Execução: {estatisticas['tempo_execucao']:.4f} segundos")
    # --- Fim Impressão Console ---

    return None, float('inf'), estatisticas


# --- Bloco Principal de Execução ---
if __name__ == "__main__":
    ARQUIVO_JSON = 'cities.json'
    RAIO_DISTANCIA = 3.5 # Exemplo de raio 'r' 
    ARQUIVO_SAIDA = "resultado_ucs.txt" # NOVO NOME para o arquivo de saída UCS

    print("Carregando dados das cidades...")
    dados_cidades = carregar_dados_cidades(ARQUIVO_JSON)

    if dados_cidades:
        print(f"Dados carregados para {len(dados_cidades)} cidades.")
        print(f"\nConstruindo grafo com raio de distância r = {RAIO_DISTANCIA}...")
        grafo = construir_grafo(dados_cidades, RAIO_DISTANCIA)
        print(f"Grafo construído.")
        num_arestas = sum(len(adj) for adj in grafo.values()) // 2
        nos_conectados = sum(1 for cidade in grafo if grafo[cidade]) 
        print(f"Número de nós com conexões: {nos_conectados} / {len(grafo)}")
        print(f"Número de arestas: {num_arestas}")

        # --- Defina os Cenários (Mesmos do exemplo anterior) ---
        cidade_inicial_1 = "New York"  
        cidade_final_1 = "Jacksonville"   
        cidade_inicial_2 = "Miami" 
        cidade_final_2 = "Seattle" 
        cidade_inicial_3 = "Los Angeles"
        cidade_final_3 = "Detroit"  
        cenarios = [
            (cidade_inicial_1, cidade_final_1),
            (cidade_inicial_2, cidade_final_2),
            (cidade_inicial_3, cidade_final_3)
        ]

        # --- Abre o Arquivo de Saída ---
        try:
            with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as outfile:
                print(f"\nArquivo '{ARQUIVO_SAIDA}' aberto para escrita dos resultados.")
                # Atualiza cabeçalho para indicar UCS
                outfile.write(f"Resultados da Busca de Custo Uniforme (UCS) (Raio: {RAIO_DISTANCIA})\n") 
                outfile.write("=============================================\n\n")

                # --- Executa para cada cenário ---
                resultados_finais = {} 
                for i, (inicio, fim) in enumerate(cenarios, 1):
                    
                    # (Impressão e escrita do cabeçalho do cenário - sem alterações)
                    print(f"\n=============================================")
                    print(f"          Executando Cenário {i}: {inicio} -> {fim} (UCS)")
                    print(f"=============================================")
                    outfile.write(f"=============================================\n")
                    outfile.write(f"          Cenário {i}: {inicio} -> {fim} (UCS)\n") # Indica UCS no arquivo
                    outfile.write(f"=============================================\n\n")

                    # (Verificação de existência das cidades - sem alterações)
                    if inicio not in dados_cidades or fim not in dados_cidades:
                         print(f"\nErro: Cenário {i} pulado. Cidade inicial '{inicio}' ou Cidade final '{fim}' não encontrada.")
                         outfile.write(f"Erro: Cidade inicial '{inicio}' ou Cidade final '{fim}' não encontrada nos dados JSON.\n\n")
                         resultados_finais[f"Cenário {i}"] = {"status": "Erro de Entrada", "message": f"Cidade '{inicio if inicio not in dados_cidades else fim}' não encontrada no JSON."}
                         continue

                    # Chama a função de busca UCS
                    caminho, custo, estatisticas = busca_custo_uniforme(grafo, dados_cidades, inicio, fim) 
                    resultados_finais[f"Cenário {i}"] = estatisticas 

                    # --- Escreve o Bloco de Resumo Final no Arquivo ---
                    outfile.write("--- Busca Finalizada ---\n")
                    outfile.write(f"Total de Expansões de Nós: {estatisticas['total_expansoes']}\n") 
                    # UCS não tem busca bidirecional, remove essas linhas
                    # outfile.write(f"Expansões (Avanço): ... \n") 
                    # outfile.write(f"Expansões (Retrocesso): ... \n") 
                    outfile.write(f"Tempo de Execução: {estatisticas['tempo_execucao']:.4f} segundos\n") 
                    if estatisticas.get("custo_final") != float('inf'): # Se um custo foi encontrado
                        outfile.write(f"Custo final calculado: {estatisticas['custo_final']:.2f}\n")
                    
                    # Mensagens sobre reconstrução não são tão relevantes para UCS pois o caminho é mantido
                    # outfile.write("Reconstruindo caminho...\n") 
                    if estatisticas["status"] == "Erro na Reconstrução": # Pouco provável em UCS, mas por segurança
                         outfile.write("Erro durante a reconstrução do caminho!\n")
                    elif not estatisticas.get("caminho"):
                        outfile.write(f"Nenhum caminho encontrado entre {inicio} e {fim}.\n")


                    outfile.write(f"\n--- Resultado Final ---\n")
                    outfile.write(f"  Status: {estatisticas['status']}\n")
                    # Usa a string detalhada se existir
                    if estatisticas.get("caminho_detalhado"): 
                        # UCS não tem nó de encontro
                        # outfile.write(f"  Nó Final de Encontro: ...\n")
                        outfile.write(f"  Caminho Encontrado ({len(estatisticas['caminho'])} cidades):\n")
                        outfile.write(f"    {estatisticas['caminho_detalhado']}\n") 
                        outfile.write(f"  Distância Total: {estatisticas['custo_final']:.2f}\n")
                    elif estatisticas["status"] == "Erro na Reconstrução": 
                        outfile.write(f"  Custo encontrado foi: {estatisticas['custo_final']:.2f}\n")
                    # Sempre escreve estas estatísticas
                    outfile.write(f"  Total de Expansões de Nós: {estatisticas['total_expansoes']}\n")
                    outfile.write(f"  Tempo de Execução: {estatisticas['tempo_execucao']:.4f} segundos\n")
                    outfile.write(f"=============================================\n\n")
                    # --- Fim do Bloco de Escrita no Arquivo para o Cenário ---

            print(f"\nResultados escritos com sucesso em '{ARQUIVO_SAIDA}'")

        except IOError as e: 
            print(f"Erro ao escrever no arquivo '{ARQUIVO_SAIDA}': {e}")
            
    else:
        print("Não foi possível carregar os dados das cidades. Abortando.")