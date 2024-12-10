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

    cambiado = True
    while cambiado:
        cambiado = False
        for no_terminal, reglas in producciones.items():
            for regla in reglas:
                print(f"\nAnalizando la producción {no_terminal} → {regla}")
                
                # Analizar cada símbolo en la regla
                for i, simbolo in enumerate(regla):
                    print(f"\nProcesando el símbolo '{simbolo}' en la posición {i}")

                    if simbolo in no_terminales:
                        resto = regla[i + 1:]  # Todo lo que sigue después del no-terminal
                        print(f"  Resto después del símbolo '{simbolo}': {resto}")

                        cadena_aux = ''  # Inicializo cadena_aux para construir la cadena después del símbolo actual
                        
                        # Recorrer el resto y construir cadena_aux
                        for char in resto:
                            cadena_aux += char
                            print(f"    Construyendo cadena_aux: '{cadena_aux}'")

                            if char in terminales:
                                print(f"      Se encontró el terminal '{char}' después de '{simbolo}'")
                                siguiente[simbolo].add(char)
                                print(f"      Agregando '{char}' a Siguiente({simbolo})")
                                cadena_aux = ''  # Reinicio cadena_aux después de encontrar un terminal
                                break
                            
                            elif char in no_terminales:
                                print(f"      Se encontró el no-terminal '{char}' después de '{simbolo}'")
                                siguiente[simbolo].update(siguiente[char])
                                print(f"      Fusionando Siguiente({char}) en Siguiente({simbolo})")
                                cadena_aux = ''  # Reinicio cadena_aux después de encontrar otro no-terminal
                                break

                        else:
                            # Si todo el resto produce ε
                            print(f"      El resto después del no-terminal '{simbolo}' produce ε")
                            siguiente[simbolo].update(siguiente[no_terminal])
                            print(f"      Fusionando Siguiente({no_terminal}) en Siguiente({simbolo})")
                            cambiado = True

                    print(f"  Siguiente({simbolo}) ahora contiene: {siguiente[simbolo]}")
                    cambiado = True

    return siguiente
def calcular_siguiente(producciones, terminales, no_terminales, simbolo_inicial, primero):
    siguiente = {nt: set() for nt in no_terminales}
    siguiente[simbolo_inicial].add("$")  # El símbolo inicial siempre incluye el fin de cadena.

    cambiado = True
    while cambiado:
        cambiado = False
        for no_terminal, reglas in producciones.items():
            for regla in reglas:
                print(f"\nAnalizando la producción {no_terminal} → {regla}")

                # Analizar símbolo por símbolo del lado derecho
                for i, simbolo in enumerate(regla):
                    if simbolo in no_terminales:
                        print(f"\nProcesando el no-terminal '{simbolo}' en la posición {i}")

                        resto = regla[i + 1:]  # Todo lo que sigue después del no-terminal
                        print(f"Resto después del símbolo '{simbolo}': {resto}")

                        cadena_aux = ''  # Iniciamos cadena_aux vacío

                        # Recorrer el resto y construir cadena_aux para compararlo con Primero
                        for char in resto:
                            cadena_aux += char
                            print(f"Construyendo cadena_aux: '{cadena_aux}'")

                            # Caso: Encontramos un terminal
                            if char in terminales:
                                print(f"Se encontró el terminal '{char}' después de '{simbolo}'")
                                siguiente[simbolo].add(char)
                                print(f"Agregando '{char}' a Siguiente({simbolo})")
                                cadena_aux = ''  # Reiniciamos cadena_aux después de encontrar terminal
                                break

                            # Caso: Encontramos otro no-terminal
                            elif char in no_terminales:
                                print(f"Se encontró el no-terminal '{char}' después de '{simbolo}'")
                                siguiente[simbolo].update(siguiente[char])
                                print(f"Fusionamos Siguiente({char}) en Siguiente({simbolo})")
                                cadena_aux = ''  # Reiniciamos cadena_aux después de otro no-terminal
                                break

                            else:
                                print(f"El resto después del no-terminal '{simbolo}' no coincide con ningún terminal ni no-terminal")
                                break

                        else:
                            # Si el resto produce epsilon
                            print(f"El resto después del no-terminal '{simbolo}' produce ε")
                            siguiente[simbolo].update(siguiente[no_terminal])
                            print(f"Fusionamos Siguiente({no_terminal}) en Siguiente({simbolo})")
                            cambiado = True

                    elif simbolo in terminales:
                        # Si el símbolo es terminal, no lo procesamos en el conjunto Siguiente
                        print(f"El símbolo '{simbolo}' es terminal y lo ignoramos.")

        print(f"\nSiguiente actual: {siguiente}")
        cambiado = True  # Reiterar hasta que no haya cambios

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