def leer_gramatica(archivo):
    producciones, terminales, no_terminales, simbolo_inicial, flag_producciones = {}, set(), set(), '', False

    try:
        with open(archivo, 'r', encoding='utf-8') as file:
            for linea in map(str.strip, file):
                if not linea:
                    continue

                if linea.startswith("V:"):
                    no_terminales.update(map(str.strip, linea[2:].split(',')))
                elif linea.startswith("T:"):
                    terminales.update(t if t else ',' for t in map(str.strip, linea[2:].split(',')))
                elif linea.startswith("S:"):
                    simbolo_inicial = linea.split(':')[1].strip()
                elif linea == "P:":
                    flag_producciones = True
                elif flag_producciones and "→" in linea:
                    try:
                        no_terminal, produccion = map(str.strip, linea.split("→"))
                        alternativas = produccion.split('|')
                        producciones.setdefault(no_terminal, []).extend(map(str.strip, alternativas))
                    except ValueError:
                        print(f"Error al procesar la producción: {linea}")

        return producciones, terminales, no_terminales, simbolo_inicial

    except FileNotFoundError:
        print(f"Error: El archivo {archivo} no se encuentra.")
        return {}, set(), set(), ''


def calcular_primero(producciones, terminales, no_terminales):
    def obtener_primero(simbolo, visited):
        if simbolo in terminales:
            return {simbolo}
        if simbolo in no_terminales and simbolo not in visited:
            visited.add(simbolo)
            resultado = set()

            for produccion in producciones.get(simbolo, []):
                i, secuencia = 0, ''
                while i < len(produccion):
                    secuencia += produccion[i]

                    if secuencia in terminales:
                        resultado.add(secuencia)
                        break
                    elif produccion[i] in no_terminales:
                        resultado |= obtener_primero(produccion[i], visited)
                        break

                    i += 1
                else:
                    resultado.add("ε")

            visited.remove(simbolo)
            return resultado

        return {simbolo}

    return {no_terminal: obtener_primero(no_terminal, set()) for no_terminal in producciones}
def calcular_siguiente(producciones, terminales, no_terminales, simbolo_inicial, primero):
    siguiente = {nt: set() for nt in no_terminales}
    siguiente[simbolo_inicial].add("$")  # El símbolo inicial siempre incluye el fin de cadena.

    # Repetir hasta que no haya cambios en los conjuntos Siguiente
    cambiado = True
    while cambiado:
        cambiado = False
        for no_terminal, reglas in producciones.items():
            for regla in reglas:
                # Analizar símbolo por símbolo del lado derecho
                for i, simbolo in enumerate(regla):
                    if simbolo in no_terminales:  # Solo para no terminales
                        resto = regla[i + 1:]  # Lo que sigue después del símbolo actual
                        
                        # Caso 1: Hay algo después de 'simbolo'
                        if resto:
                            primer_resto = set()
                            j = 0
                            while j < len(resto):
                                parte = resto[j]
                                if parte in terminales:
                                    primer_resto.add(parte)
                                    break
                                elif parte in no_terminales:
                                    primer_resto.update(primero[parte] - {"ε"})
                                    if "ε" not in primero[parte]:
                                        break
                                j += 1
                            else:
                                primer_resto.add("ε")
                            
                            # Agregar a Siguiente(simbolo) todo Primero(resto) sin ε
                            nuevo = primer_resto - {"ε"}
                            if not nuevo.issubset(siguiente[simbolo]):
                                siguiente[simbolo].update(nuevo)
                                cambiado = True

                        # Caso 2: No hay nada después de 'simbolo' o el resto genera ε
                        if not resto or "ε" in primer_resto:
                            # Agregar Siguiente(no_terminal) a Siguiente(simbolo)
                            if not siguiente[no_terminal].issubset(siguiente[simbolo]):
                                siguiente[simbolo].update(siguiente[no_terminal])
                                cambiado = True

    return siguiente








def imprimir_gramatica(producciones):
    print("\nReglas de Producción Separadas:")
    for no_terminal, reglas in producciones.items():
        for i, produccion in enumerate(reglas, 1):
            print(f"{no_terminal} → {produccion} (Regla {i})")


def imprimir_conjunto(conjunto, nombre):
    print(f"\n{nombre}:", conjunto)


def imprimir_primero(primero):
    print("\nConjunto Primero:")
    for no_terminal, conjunto in primero.items():
        print(f"Primero({no_terminal}): {conjunto}")


def imprimir_siguiente(siguiente):
    print("\nConjunto Siguiente:")
    for no_terminal, conjunto in siguiente.items():
        print(f"Siguiente({no_terminal}): {conjunto}")


# Programa principal
archivo_gramatica = "gramatica.txt"
producciones, terminales, no_terminales, simbolo_inicial = leer_gramatica(archivo_gramatica)

print(f"\nSímbolo inicial: {simbolo_inicial}")
imprimir_conjunto(terminales, "Terminales")
imprimir_conjunto(no_terminales, "No Terminales")
imprimir_gramatica(producciones)

print("\nCalculando Conjunto Primero...")
primero = calcular_primero(producciones, terminales, no_terminales)
imprimir_primero(primero)

print("\nCalculando Conjunto Siguiente...")
siguiente = calcular_siguiente(producciones, terminales, no_terminales, simbolo_inicial, primero)
imprimir_siguiente(siguiente)