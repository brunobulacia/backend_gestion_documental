def validar_estructura_flujo(nodos, transiciones):
    # Construir el grafo
    from collections import defaultdict, deque

    grafo = defaultdict(list)
    ids_nodos = set()
    nodos_por_id = {}
    nodos_inicio = []
    nodos_fin = []

    for nodo in nodos:
        nodo_id = nodo["id"]
        ids_nodos.add(nodo_id)
        nodos_por_id[nodo_id] = nodo
        if nodo["tipo"] == "start":
            nodos_inicio.append(nodo_id)
        elif nodo["tipo"] == "end":
            nodos_fin.append(nodo_id)

    for trans in transiciones:
        origen = trans["origen"]
        destino = trans["destino"]
        grafo[origen].append(destino)

    # Validación de nodos de inicio y fin
    if len(nodos_inicio) != 1:
        return False, "Debe haber exactamente un nodo de inicio."
    if len(nodos_fin) < 1:
        return False, "Debe haber al menos un nodo de fin."

    # Verificar ciclos con DFS
    def tiene_ciclo(nodo, visitados, en_pila):
        visitados.add(nodo)
        en_pila.add(nodo)
        for vecino in grafo[nodo]:
            if vecino not in visitados:
                if tiene_ciclo(vecino, visitados, en_pila):
                    return True
            elif vecino in en_pila:
                return True
        en_pila.remove(nodo)
        return False

    visitados = set()
    if tiene_ciclo(nodos_inicio[0], visitados, set()):
        return False, "El flujo contiene un ciclo infinito."

    # Verificar conectividad (todos los nodos alcanzables desde inicio)
    def bfs(inicio):
        visitados = set()
        queue = deque([inicio])
        while queue:
            actual = queue.popleft()
            visitados.add(actual)
            for vecino in grafo[actual]:
                if vecino not in visitados:
                    queue.append(vecino)
        return visitados

    alcanzables = bfs(nodos_inicio[0])
    if ids_nodos - alcanzables:
        return False, "Hay nodos que no son alcanzables desde el inicio."

    # Verificar si hay camino a algún nodo de fin desde el inicio
    if not any(fin in alcanzables for fin in nodos_fin):
        return False, "No hay camino desde el inicio hacia un nodo de fin."

    return True, "Flujo válido."
