def leer_gramatica(archivo):
    producciones, terminales, no_terminales, simbolo_inicial, flag_producciones = {}, set(), [], '', False

    try:
        with open(archivo, 'r', encoding='utf-8') as file:
            for linea in map(str.strip, file):
                if not linea:
                    continue

                if linea.startswith("V:"):
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

def calcular_siguiente(producciones, terminales, no_terminales, simbolo_inicial, primero):
    siguiente = {nt: set() for nt in no_terminales}
    siguiente[simbolo_inicial].add("$")

    for no_terminal in no_terminales:
        for produccion_no_terminal, reglas in producciones.items():
            for regla in reglas:
                for i in range(len(regla)):
                    simbolo = regla[i]
                    if i + 1 < len(regla) and regla[i + 1] == "'":
                        simbolo += "'"

                    if simbolo == no_terminal:
                        resto = regla[i + len(simbolo):]
                        for j in range(len(resto)):
                            siguiente_simbolo = resto[j]
                            if j + 1 < len(resto) and resto[j + 1] == "'":
                                siguiente_simbolo += "'"

                            if siguiente_simbolo in terminales:
                                siguiente[no_terminal].add(siguiente_simbolo)
                                break
                            elif siguiente_simbolo in no_terminales:
                                primero_sin_epsilon = primero[siguiente_simbolo] - {"ε"}
                                siguiente[no_terminal].update(primero_sin_epsilon)
                                if "ε" not in primero[siguiente_simbolo]:
                                    break
                        else:
                            siguiente[no_terminal].update(siguiente[produccion_no_terminal])
    return siguiente

def imprimir_gramatica(producciones):
    for no_terminal, reglas in producciones.items():
        for produccion in reglas:
            print(f"{no_terminal} → {produccion}")

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
    tabla_ll1 = {no_terminal: {terminal: "-" for terminal in terminales.union({"$"})} for no_terminal in no_terminales}

    for no_terminal, reglas in producciones.items():
        for regla in reglas:
            acumulador = ""
            for i, simbolo in enumerate(regla):
                acumulador += simbolo
                if acumulador in terminales:
                    if tabla_ll1[no_terminal][acumulador] == "-":
                        tabla_ll1[no_terminal][acumulador] = f"{no_terminal} → {regla}"
                    break
                elif acumulador in no_terminales:
                    primero_acumulador = primero.get(acumulador, set())
                    for terminal in primero_acumulador - {"ε"}:
                        if tabla_ll1[no_terminal][terminal] == "-":
                            tabla_ll1[no_terminal][terminal] = f"{no_terminal} → {regla}"
                    if "ε" not in primero_acumulador:
                        break
                    acumulador = ""
            if "ε" in regla:
                for terminal_s in siguiente.get(no_terminal, set()):
                    if tabla_ll1[no_terminal][terminal_s] == "-":
                        tabla_ll1[no_terminal][terminal_s] = f"{no_terminal} → ε"
    return tabla_ll1

def imprimir_tabla_ll1(tabla_ll1, terminales, no_terminales):
    terminales_ordenados = sorted(list(terminales)) + ["$"]
    encabezado = "No-Terminal".ljust(15) + " | " + " | ".join(t.ljust(15) for t in terminales_ordenados)
    separador = "-" * len(encabezado)
    print(encabezado)
    print(separador)
    for no_terminal in no_terminales:
        fila = no_terminal.ljust(15) + " | " + " | ".join(
            (str(tabla_ll1[no_terminal].get(t, "-"))).ljust(15)
            for t in terminales_ordenados
        )
        print(fila)

import re

def tokenizar(cadena):
    token_specification = [
        ('PLUS', r'\+'),         # Suma
        ('MINUS', r'-'),         # Resta
        ('MULT', r'\*'),         # Multiplicación
        ('DIV', r'/'),           # División
        ('LPAREN', r'\('),       # Paréntesis izquierdo
        ('RPAREN', r'\)'),       # Paréntesis derecho
        ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),  # Identificadores y variables
        ('NUMBER', r'\d+'),      # Números
        ('HASH', r'#'),          # Símbolo #
        ('SKIP', r'[ \t]+'),     # Espacios y tabulaciones
        ('MISMATCH', r'.'),      # Otros caracteres inesperados
    ]

    tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
    tokens = []
    for mo in re.finditer(tok_regex, cadena):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} inesperado')
        if kind in ['ID', 'NUMBER']:
            kind = 'id'
        elif kind == 'PLUS':
            kind = '+'
        elif kind == 'MINUS':
            kind = '-'
        elif kind == 'MULT':
            kind = '*'
        elif kind == 'DIV':
            kind = '/'
        elif kind == 'LPAREN':
            kind = '('
        elif kind == 'RPAREN':
            kind = ')'
        tokens.append(kind)
    return tokens

def analizar_ll1(tokens, tabla_ll1, simbolo_inicial, terminales, no_terminales, cadenaAux):
    pila, cadena = ['$'], tokens + ['$']
    pila.append(simbolo_inicial)

    # Establecemos anchos fijos para cada columna
    print(f"{'Coincidencia':<30} | {'Pila':<30} | {'Cadena':<30} | {'Salida':<15}")
    print(f"{'-'*30} | {'-'*30} | {'-'*30} | {'-'*15}")
    print(f"{'':<30} | {' '.join(pila):<30} | {' '.join(cadena):<30} | {'':<15}")

    while pila:
        top_pila, top_cadena = pila.pop().strip(), cadena[0].strip() if cadena else None
        coincidencia = f"{top_pila}, {top_cadena}"

        if top_pila == top_cadena:
            cadena.pop(0)
            print(f"{coincidencia:<30} | {' '.join(pila):<30} | {' '.join(cadena):<30} | {top_pila:<15}")
        elif top_pila in no_terminales:
            produccion = tabla_ll1.get(top_pila, {}).get(top_cadena, None)
            if produccion and produccion != "-":
                _, regla = produccion.split("→")
                regla = regla.strip()

                # Insertamos los símbolos de la regla en la pila
                if regla not in ("", "ε"):
                    simbolos, i = [], 0
                    while i < len(regla):
                        mejor_match = max(
                            (simbolo for conjunto in [terminales, no_terminales] for simbolo in conjunto if regla.startswith(simbolo, i)),
                            key=len, default=None
                        )
                        if mejor_match:
                            simbolos.append(mejor_match)
                            i += len(mejor_match) - 1
                        i += 1
                    pila.extend(reversed(simbolos))

                # Imprimimos después de actualizar la pila
                print(f"{coincidencia:<30} | {' '.join(pila):<30} | {' '.join(cadena):<30} | {produccion:<15}")
            else:
                print(f"{coincidencia:<30} | {' '.join(pila):<30} | {' '.join(cadena):<30} | {'No hay producción válida':<15}")
                print("\n{} no es aceptada".format("".join(cadenaAux)))
                return False
        else:
            print(f"{coincidencia:<30} | {' '.join(pila):<30} | {' '.join(cadena):<30} | {'Símbolo inesperado':<15}")
            print("\n{} no es aceptada".format("".join(cadenaAux)))
            return False

    print("\n{} Es aceptada. Expresión válida".format("".join(cadenaAux)))
    return True



archivo_gramatica = "gramatica.txt"
producciones, terminales, no_terminales, simbolo_inicial = leer_gramatica(archivo_gramatica)

print(f"\nSímbolo inicial: {simbolo_inicial}")
imprimir_conjunto(terminales, "Terminales")
imprimir_conjunto(no_terminales, "No Terminales")
imprimir_gramatica(producciones)

primero = calcular_primero(producciones, terminales, no_terminales)
imprimir_primero(primero)

siguiente = calcular_siguiente(producciones, terminales, no_terminales, simbolo_inicial, primero)
imprimir_siguiente(siguiente)

tabla_ll1 = generar_tabla_ll1(producciones, terminales, no_terminales, primero, siguiente)
imprimir_tabla_ll1(tabla_ll1, terminales, no_terminales)

cadena = input("Ingresa una cadena para analizar: ")
tokens = tokenizar(cadena)
analizar_ll1(tokens, tabla_ll1, simbolo_inicial, terminales, no_terminales, cadena)