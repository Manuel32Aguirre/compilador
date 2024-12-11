def leer_gramatica(archivo):
    producciones, terminales, no_terminales, simbolo_inicial, flag_producciones = {}, set(), [], '', False

    try:
        with open(archivo, 'r', encoding='utf-8') as file:
            for linea in map(str.strip, file):
                if not linea:
                    continue

                if linea.startswith("V:"):
                    # Añadir no-terminales en orden
                    nuevos_no_terminales = map(str.strip, linea[2:].split(','))
                    for nt in nuevos_no_terminales:
                        if nt not in no_terminales:
                            no_terminales.append(nt)

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
        return {}, set(), [], ''




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



    return siguiente
def calcular_siguiente(producciones, terminales, no_terminales, simbolo_inicial, primero):
    # Inicializar conjuntos Siguiente, con `$` solo para el símbolo inicial
    siguiente = {nt: set() for nt in no_terminales}
    siguiente[simbolo_inicial].add("$")  # Agregar `$` únicamente al símbolo inicial

    iteracion = 1
    cambiado = True
    max_iteraciones = 100  # Evitar bucles infinitos

    while cambiado and iteracion < max_iteraciones:
        iteracion += 1
        cambiado = False

        for no_terminal in no_terminales:
            anterior = siguiente[no_terminal].copy()  # Copia del estado anterior para verificar cambios

            # Recorrer todas las producciones para buscar el no_terminal
            for produccion_no_terminal, reglas in producciones.items():
                for regla in reglas:
                    if no_terminal in regla:
                        resto = regla[regla.index(no_terminal) + 1:]

                        acumulado = ''
                        for char in resto:
                            acumulado += char

                            if acumulado in terminales:
                                siguiente[no_terminal].add(acumulado)
                                cambiado = True
                                break

                            elif acumulado in no_terminales:
                                primero_sin_epsilon = primero[acumulado] - {"ε"}
                                if primero_sin_epsilon - siguiente[no_terminal]:
                                    siguiente[no_terminal].update(primero_sin_epsilon)
                                    cambiado = True

                                if "ε" not in primero[acumulado]:
                                    break

                        if not resto or all("ε" in primero[s] for s in resto if s in no_terminales):
                            siguiente_a_fusionar = siguiente[produccion_no_terminal] - {"$"}
                            if siguiente_a_fusionar - siguiente[no_terminal]:
                                siguiente[no_terminal].update(siguiente_a_fusionar)
                                cambiado = True

            if siguiente[no_terminal] != anterior:
                cambiado = True

        if not cambiado:
            break

        iteracion += 1

    if iteracion >= max_iteraciones:
        return siguiente

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

def generar_tabla_ll1(producciones, terminales, no_terminales, primero, siguiente):
    # Inicializar la tabla LL(1) vacía con `"-"` en lugar de `None`
    tabla_ll1 = {no_terminal: {terminal: "-" for terminal in terminales.union({"$"})} for no_terminal in no_terminales}

    # Iterar sobre cada no-terminal y sus reglas de producción
    for no_terminal, reglas in producciones.items():
        print(f"\nAnalizando las reglas de producción para: {no_terminal}")
        for regla in reglas:
            print(f"  Regla de producción: {no_terminal} → {regla}")

            # Inicializar un acumulador para construir terminales o no terminales
            acumulador = ""
            for i, simbolo in enumerate(regla):
                acumulador += simbolo  # Construir símbolo concatenando
                if acumulador in terminales:
                    print(f"    Tupla generada: M[{no_terminal}, {acumulador}] = {no_terminal} → {regla}")
                    if tabla_ll1[no_terminal][acumulador] == "-":
                        tabla_ll1[no_terminal][acumulador] = f"{no_terminal} → {regla}"
                    break
                elif acumulador in no_terminales:
                    primero_acumulador = primero.get(acumulador, set())
                    for terminal in primero_acumulador - {"ε"}:
                        print(f"    Tupla generada: M[{no_terminal}, {terminal}] = {no_terminal} → {regla}")
                        if tabla_ll1[no_terminal][terminal] == "-":
                            tabla_ll1[no_terminal][terminal] = f"{no_terminal} → {regla}"
                    if "ε" not in primero_acumulador:
                        break
                    acumulador = ""  # Reiniciar acumulador tras procesar no-terminal
                elif i == len(regla) - 1:
                    print(f"    ADVERTENCIA: No se encontró un terminal o no-terminal válido para '{acumulador}'. Ignorando la regla.")

            # ** Manejo especial para el caso de ε (producción vacía)**
            if "ε" in regla:
                for terminal_s in siguiente.get(no_terminal, set()):
                    print(f"    Tupla generada: M[{no_terminal}, {terminal_s}] = {no_terminal} → ε")
                    if tabla_ll1[no_terminal][terminal_s] == "-":
                        tabla_ll1[no_terminal][terminal_s] = f"{no_terminal} → ε"

    return tabla_ll1


def imprimir_tabla_ll1(tabla_ll1, terminales, no_terminales):
    print("\nTabla LL(1):")

    # Ordenar terminales y agregar '$' al final como marcador de fin de cadena
    terminales_ordenados = sorted(list(terminales)) + ["$"]

    # Encabezado de la tabla con columnas más anchas (15 caracteres)
    encabezado = "No-Terminal".ljust(15) + " | " + " | ".join(t.ljust(15) for t in terminales_ordenados)
    separador = "-" * len(encabezado)
    print(encabezado)
    print(separador)

    # Imprimir cada fila respetando el orden de no-terminales como aparecen en la lista original
    for no_terminal in no_terminales:
        fila = no_terminal.ljust(15) + " | " + " | ".join(
            (str(tabla_ll1[no_terminal].get(t, "-"))).ljust(15)
            for t in terminales_ordenados
        )
        print(fila)




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

print("\nGenerando y mostrando la tabla LL(1)...")
tabla_ll1 = generar_tabla_ll1(producciones, terminales, no_terminales, primero, siguiente)
imprimir_tabla_ll1(tabla_ll1, terminales, no_terminales)