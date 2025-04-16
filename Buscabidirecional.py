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

def reconstruir_caminho(no_inicial, no_final, no_encontro, pais_avanco, pais_retrocesso):
    # (Função sem alterações)
    caminho = []
    atual = no_encontro
    while atual is not None:
        caminho.append(atual)
        atual = pais_avanco.get(atual)
    caminho.reverse() 
    atual = pais_retrocesso.get(no_encontro) 
    while atual is not None:
        caminho.append(atual)
        atual = pais_retrocesso.get(atual)
    if not caminho:
        if no_inicial == no_final and no_encontro == no_inicial: return [no_inicial]
        else: return None 
    if caminho[0] != no_inicial: return None 
    if caminho[-1] != no_final and not (no_encontro == no_final and pais_retrocesso.get(no_encontro) is None):
        return None 
    return caminho

# --- Busca Bidirecional (Com caminho detalhado) ---

def busca_bidirecional_final_verbose(grafo, dados_cidades, no_inicial, no_final):
    """
    Executa a Busca Bidirecional, imprime resumo final detalhado no console
    (incluindo distâncias dos segmentos do caminho) e retorna estatísticas.
    """
    print(f"\n--- Iniciando Busca Bidirecional: {no_inicial} -> {no_final} ---")
    inicio_tempo = time.time()

    estatisticas = {
        "total_expansoes": 0, "expansoes_avanco": 0, "expansoes_retrocesso": 0,
        "no_encontro": None, "custo_final": float('inf'), 
        "caminho": None, 
        "caminho_detalhado": "", # Nova chave para a string do caminho com distâncias
        "tempo_execucao": 0, "status": "Não Iniciado"
    }

    # (Tratamento inicial de erros e caso base - sem alterações)
    if no_inicial == no_final:
        print("Nó inicial é o mesmo que o nó final.")
        estatisticas.update({"status": "Inicial igual ao Final", "caminho": [no_inicial], "custo_final": 0, "tempo_execucao": time.time() - inicio_tempo, "caminho_detalhado": no_inicial})
        return [no_inicial], 0, estatisticas
    if no_inicial not in grafo or no_final not in grafo:
        print(f"Erro: Nó inicial '{no_inicial}' ou Nó final '{no_final}' não está na conectividade do grafo.")
        estatisticas.update({"status": "Nó Inicial ou Final fora do grafo", "tempo_execucao": time.time() - inicio_tempo})
        return None, float('inf'), estatisticas
        
    # (Inicialização das filas, visitados, pais - sem alterações)
    fila_prio_avanco = [(0, dados_cidades[no_inicial]['population'], no_inicial)]
    visitados_avanco = {no_inicial: 0}; pais_avanco = {no_inicial: None}
    fila_prio_retrocesso = [(0, dados_cidades[no_final]['population'], no_final)]
    visitados_retrocesso = {no_final: 0}; pais_retrocesso = {no_final: None}
    custo_total_minimo = float('inf'); no_encontro = None

    # --- Loop Principal da Busca (Impressões moderadas no console - sem alterações) ---
    while fila_prio_avanco and fila_prio_retrocesso:
        custo_min_avanco = fila_prio_avanco[0][0]; custo_min_retrocesso = fila_prio_retrocesso[0][0]
        if custo_min_avanco + custo_min_retrocesso >= custo_total_minimo:
            print(f"\nCondição de término atingida: min_avanco ({custo_min_avanco:.2f}) + min_retrocesso ({custo_min_retrocesso:.2f}) >= melhor_custo ({custo_total_minimo:.2f})")
            estatisticas["status"] = "Caminho ótimo encontrado"
            break 
        
        if len(fila_prio_avanco) <= len(fila_prio_retrocesso): # Expande Avanço
            if not fila_prio_avanco: continue
            custo_f, _, atual_f = heapq.heappop(fila_prio_avanco)
            if custo_f > visitados_avanco[atual_f]: continue 
            estatisticas["total_expansoes"] += 1; estatisticas["expansoes_avanco"] += 1
            print(f"  [{estatisticas['total_expansoes']:<4} AVN] Expandir: {atual_f:<15} (Custo: {custo_f:.2f})")
            if atual_f in visitados_retrocesso:
                custo_total = custo_f + visitados_retrocesso[atual_f]
                if custo_total < custo_total_minimo:
                    print(f"    **** Novo MELHOR caminho! Encontro: {atual_f}, Custo: {custo_total:.2f} (Ant: {custo_total_minimo:.2f}) ****")
                    custo_total_minimo = custo_total; no_encontro = atual_f
            for vizinho, distancia in grafo.get(atual_f, []):
                novo_custo_f = custo_f + distancia
                if vizinho not in visitados_avanco or novo_custo_f < visitados_avanco[vizinho]:
                    visitados_avanco[vizinho] = novo_custo_f; pais_avanco[vizinho] = atual_f
                    heapq.heappush(fila_prio_avanco, (novo_custo_f, dados_cidades[vizinho]['population'], vizinho))
        else: # Expande Retrocesso
            if not fila_prio_retrocesso: continue
            custo_b, _, atual_b = heapq.heappop(fila_prio_retrocesso)
            if custo_b > visitados_retrocesso[atual_b]: continue 
            estatisticas["total_expansoes"] += 1; estatisticas["expansoes_retrocesso"] += 1
            print(f"  [{estatisticas['total_expansoes']:<4} RET] Expandir: {atual_b:<15} (Custo: {custo_b:.2f})")
            if atual_b in visitados_avanco:
                custo_total = custo_b + visitados_avanco[atual_b]
                if custo_total < custo_total_minimo:
                     print(f"    **** Novo MELHOR caminho! Encontro: {atual_b}, Custo: {custo_total:.2f} (Ant: {custo_total_minimo:.2f}) ****")
                     custo_total_minimo = custo_total; no_encontro = atual_b
            for vizinho, distancia in grafo.get(atual_b, []):
                novo_custo_b = custo_b + distancia
                if vizinho not in visitados_retrocesso or novo_custo_b < visitados_retrocesso[vizinho]:
                    visitados_retrocesso[vizinho] = novo_custo_b; pais_retrocesso[vizinho] = atual_b 
                    heapq.heappush(fila_prio_retrocesso, (novo_custo_b, dados_cidades[vizinho]['population'], vizinho))

    # --- Fim do Loop da Busca ---
    fim_tempo = time.time()
    estatisticas["tempo_execucao"] = fim_tempo - inicio_tempo

    # --- Prepara Resumo Final (Impressão no Console) ---
    print("\n--- Busca Finalizada ---")
    # (Impressão das estatísticas gerais - sem alterações)
    print(f"Total de Expansões de Nós: {estatisticas['total_expansoes']}") 
    print(f"Expansões (Avanço): {estatisticas['expansoes_avanco']}") 
    print(f"Expansões (Retrocesso): {estatisticas['expansoes_retrocesso']}") 
    print(f"Tempo de Execução: {estatisticas['tempo_execucao']:.4f} segundos") 

    if no_encontro:
        print(f"Melhor caminho encontrado com encontro no nó: {no_encontro}") 
        print(f"Custo final calculado: {custo_total_minimo:.2f}")
        print("Reconstruindo caminho...")
        caminho = reconstruir_caminho(no_inicial, no_final, no_encontro, pais_avanco, pais_retrocesso)
        
        if caminho: 
            print("Reconstrução do caminho bem-sucedida.") 
            estatisticas.update({"caminho": caminho, "custo_final": custo_total_minimo, "no_encontro": no_encontro})
            if estatisticas["status"] == "Não Iniciado": estatisticas["status"] = "Caminho encontrado (Terminou por fila vazia)"

            # --- NOVO: Formata Caminho com Distâncias ---
            partes_caminho_str = [caminho[0]] # Começa com a primeira cidade
            for i in range(len(caminho) - 1):
                cidade_atual = caminho[i]
                proxima_cidade = caminho[i+1]
                # Busca a distância no grafo
                distancia_segmento = None
                if cidade_atual in grafo:
                     adj_list = grafo[cidade_atual]
                     dist_tuple = next((item for item in adj_list if item[0] == proxima_cidade), None)
                     if dist_tuple:
                          distancia_segmento = dist_tuple[1]
                
                if distancia_segmento is not None:
                     # Adiciona seta -> próxima cidade (Dist: valor km)
                     partes_caminho_str.append(f"-> {proxima_cidade} (Dist: {distancia_segmento:.2f})") 
                else:
                     partes_caminho_str.append(f"-> {proxima_cidade} (Dist: ??)") # Se falhar em achar
            
            estatisticas["caminho_detalhado"] = " ".join(partes_caminho_str)
            # --- FIM: Formata Caminho com Distâncias ---

            # --- Imprime Bloco de Resultado Final no Console (USA CAMINHO DETALHADO) ---
            print(f"\n--- Resultado Final ---")
            print(f"  Status: {estatisticas['status']}")
            print(f"  Nó Final de Encontro: {estatisticas['no_encontro']}")
            # Usa a string formatada aqui
            print(f"  Caminho Encontrado ({len(caminho)} cidades):")
            # Adiciona lógica de truncamento se desejar, aplicada à string detalhada
            print(f"    {estatisticas['caminho_detalhado']}") 
            print(f"  Distância Total: {estatisticas['custo_final']:.2f}")
            print(f"  Total de Expansões de Nós: {estatisticas['total_expansoes']}")
            print(f"  Tempo de Execução: {estatisticas['tempo_execucao']:.4f} segundos")
            # --- Fim do Bloco de Resultado Final ---
            
            return caminho, custo_total_minimo, estatisticas
        else: # Falha na reconstrução
            print("Erro durante a reconstrução do caminho!")
            estatisticas.update({"status": "Erro na Reconstrução", "custo_final": custo_total_minimo, "no_encontro": no_encontro})
            # (Impressão do bloco de erro - sem alterações, não tem caminho para detalhar)
            print(f"\n--- Resultado Final ---")
            print(f"  Status: {estatisticas['status']}")
            print(f"  Nó de Encontro foi: {estatisticas['no_encontro']}")
            print(f"  Custo encontrado foi: {estatisticas['custo_final']:.2f}")
            # ... resto das stats
            return None, custo_total_minimo, estatisticas 
    else: # Nenhum caminho encontrado
        # (Atualização de status e impressão do bloco "sem caminho" - sem alterações)
        if not fila_prio_avanco or not fila_prio_retrocesso and estatisticas["status"] == "Não Iniciado": estatisticas["status"] = "Nenhum caminho encontrado (Espaço de busca esgotado)"
        elif estatisticas["status"] == "Não Iniciado": estatisticas["status"] = "Nenhum caminho encontrado (Término desconhecido)"
        print(f"Nenhum caminho encontrado entre {no_inicial} e {no_final}.")
        print(f"\n--- Resultado Final ---")
        print(f"  Status: {estatisticas['status']}")
        # ... resto das stats
        return None, float('inf'), estatisticas


# --- Bloco Principal de Execução ---
if __name__ == "__main__":
    ARQUIVO_JSON = 'cities.json'
    RAIO_DISTANCIA = 3.5 # Exemplo de raio 'r' 
    ARQUIVO_SAIDA = "resultadobi.txt" 

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

        # --- Defina os Cenários (SUBSTITUA PELAS SUAS CIDADES) ---
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
                outfile.write(f"Resultados da Busca Bidirecional (Raio: {RAIO_DISTANCIA})\n")
                outfile.write("=============================================\n\n")

                # --- Executa para cada cenário ---
                resultados_finais = {} 
                for i, (inicio, fim) in enumerate(cenarios, 1):
                    
                    # (Impressão e escrita do cabeçalho do cenário - sem alterações)
                    print(f"\n=============================================")
                    print(f"          Executando Cenário {i}: {inicio} -> {fim}")
                    print(f"=============================================")
                    outfile.write(f"=============================================\n")
                    outfile.write(f"          Cenário {i}: {inicio} -> {fim}\n")
                    outfile.write(f"=============================================\n\n")

                    # (Verificação de existência das cidades - sem alterações)
                    if inicio not in dados_cidades or fim not in dados_cidades:
                         print(f"\nErro: Cenário {i} pulado. Cidade inicial '{inicio}' ou Cidade final '{fim}' não encontrada.")
                         outfile.write(f"Erro: Cidade inicial '{inicio}' ou Cidade final '{fim}' não encontrada nos dados JSON.\n\n")
                         resultados_finais[f"Cenário {i}"] = {"status": "Erro de Entrada", "message": f"Cidade '{inicio if inicio not in dados_cidades else fim}' não encontrada no JSON."}
                         continue

                    # Chama a função de busca (que imprime no console)
                    caminho, custo, estatisticas = busca_bidirecional_final_verbose(grafo, dados_cidades, inicio, fim) 
                    resultados_finais[f"Cenário {i}"] = estatisticas 

                    # --- Escreve o Bloco de Resumo Final no Arquivo (USA CAMINHO DETALHADO) ---
                    outfile.write("--- Busca Finalizada ---\n")
                    # (Escrita das estatísticas gerais - sem alterações)
                    outfile.write(f"Total de Expansões de Nós: {estatisticas['total_expansoes']}\n") 
                    outfile.write(f"Expansões (Avanço): {estatisticas['expansoes_avanco']}\n") 
                    outfile.write(f"Expansões (Retrocesso): {estatisticas['expansoes_retrocesso']}\n") 
                    outfile.write(f"Tempo de Execução: {estatisticas['tempo_execucao']:.4f} segundos\n\n") 

                    if estatisticas["no_encontro"]: 
                        outfile.write(f"Melhor caminho encontrado com encontro no nó: {estatisticas['no_encontro']}\n") 
                        outfile.write(f"Custo final calculado: {estatisticas['custo_final']:.2f}\n")
                        outfile.write("Reconstruindo caminho...\n")
                        if estatisticas["status"] == "Erro na Reconstrução":
                             outfile.write("Erro durante a reconstrução do caminho!\n")
                        # Verifica se a string detalhada existe (implica reconstrução ok)
                        elif estatisticas.get("caminho_detalhado"): 
                             outfile.write("Reconstrução do caminho bem-sucedida.\n")
                    elif estatisticas["status"] not in ["Inicial igual ao Final", "Nó Inicial ou Final fora do grafo"]:
                         outfile.write(f"Nenhum caminho encontrado entre {inicio} e {fim}.\n")

                    # Escreve o bloco "Resultado Final"
                    outfile.write(f"\n--- Resultado Final ---\n")
                    outfile.write(f"  Status: {estatisticas['status']}\n")
                    # Usa a string detalhada se existir e for aplicável
                    if estatisticas.get("caminho_detalhado") and estatisticas["status"] not in ["Erro na Reconstrução", "Inicial igual ao Final", "Nó Inicial ou Final fora do grafo"]: 
                        outfile.write(f"  Nó Final de Encontro: {estatisticas['no_encontro']}\n")
                        outfile.write(f"  Caminho Encontrado ({len(estatisticas['caminho'])} cidades):\n")
                        # Adiciona lógica de truncamento se desejar
                        outfile.write(f"    {estatisticas['caminho_detalhado']}\n") 
                        outfile.write(f"  Distância Total: {estatisticas['custo_final']:.2f}\n")
                    elif estatisticas["status"] == "Erro na Reconstrução": 
                         outfile.write(f"  Nó de Encontro foi: {estatisticas['no_encontro']}\n")
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