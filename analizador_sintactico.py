from analizador_lexico import tokenize
# Variables globales para el parser
current_pos = 0
tokens = []
tabla_simbolos = {}
# nombre_var   tipo   valor

# Devuelve una tupla con el token actual y su gramatica o None si se han procesado todos los tokens.
def current_token():
    global current_pos, tokens
    return tokens[current_pos] if current_pos < len(tokens) else None

# Verifica si el token en la posicion actual y el esperado hacen match, si si consume un token esperado y devuelve una tupla.
def match(expected_type):
    global current_pos # "global" permite modificar la vairable global
    token = current_token()
    if token and token[0] == expected_type:
        current_pos += 1
        return token
    raise SyntaxError(f"Se esperaba {expected_type}, pero se encontró {token} en la posicion {current_pos}") 

# Regla de producción inicial de la gramatica: programa completo.
def parse_program():
    tabla_simbolos["main"] = {
        "argumentos": []
    }
    
    while current_token() and current_token()[1] != "main":  # Leer prototipos de funciones
        parse_function_decl()
    while current_token():  # Leer funciones
        parse_func()

# Regla para prototipos de funciones.
def parse_function_decl():
    func_type = match("TYPE")[1]
    name = match("IDENTIFIER")[1]  # Nombre de la función
    match("LPAREN")
    args = parse_function_args()  # Procesar los argumentos
    match("RPAREN")
    match("SEMICOLON")
    tabla_simbolos[name] = {
        "argumentos" : args,
        "tipo" : func_type
    }

# Regla para procesar los argumentos de el prototipo de una funcion. tupla(tipo, nombre)
def parse_function_args():
    args = []
    if current_token()[0] == "RPAREN":  # Sin argumentos
        return args
    while current_token() and current_token()[0] != "RPAREN":
        arg_type = match("TYPE")[1]  # Tipo de dato
        if current_token()[0] == "IDENTIFIER":  # Nombre del argumento (opcional)
            arg_name = match("IDENTIFIER")[1]
            args.append((arg_type, arg_name))
        else:  # Argumento solo con tipo
            args.append((arg_type, ""))

        if current_token()[0] == "COMMA":  # Más argumentos
            match("COMMA")
        else:
            break
    return args

# Regla de produccion para una funcion nombre(){...}
def parse_func():
    if current_token()[1] != "main":
        match("TYPE")[1]
    name = match("IDENTIFIER")[1]
    match("LPAREN")
    parse_arguments(name)
    match("RPAREN")
    match("LBRACE")
    parse_statements()
    match("RBRACE")

# Regla para argumentos de función.
def parse_arguments(name):
    args = parse_function_args()
    i = 0
    if len(args) == len(tabla_simbolos[name]["argumentos"]):
        for a in args:
            if a[0] == tabla_simbolos[name]["argumentos"][i][0]:
                i+=1
            else: 
                raise SyntaxError(f"Error en asignación o llamada: {name} en la posicion {current_pos}.\nSe esperaba{name}{tabla_simbolos[name]["argumentos"]}")
        return
    else: 
        raise SyntaxError(f"Error en asignación o llamada: {name} en la posicion {current_pos}.\nSe esperaba{name}{tabla_simbolos[name]["argumentos"]}")

# Regla para cada instrucción de una funcion
def parse_statements():
    while current_token() and current_token()[0] != "RBRACE": # mientras haya tokens por consumir y no se trate de '}' #¿Esto funciona para for(){expresiones}
        parse_statement()

# Clasifica si una instrucciones es una declaracion de variable, una asignación, una llamada a una funcion o una estructura if, for o while
def parse_statement():
    """Regla para una sentencia: declaración, asignación o control."""
    token = current_token()
    if token[0] == "TYPE": 
        parse_var_decl()
    elif token[0] == "PLAY":
        # Funcion predefinida por el lenguaje
        parse_play()
    elif token[0] == "SET_TEMPO":
        # Funcion predefinida por el lenguaje
        parse_set_tempo()
    elif token[0] == "IF":
        parse_if()
    elif token[0] == "FOR":
        parse_for()
    elif token[0] == "WHILE":
        parse_while()
    elif token[0] == "IDENTIFIER": 
        parse_assignment_or_call()
    else:
        raise SyntaxError(f"Sentencia no válida: {token} posicion {current_pos}" )

# Regla para declaración de variables. 
def parse_var_decl():
    var_type = match("TYPE")[1]
    name = match("IDENTIFIER")[1]
    match("ASSIGN")
    if current_token()[0] == "STRING":
        value = match("STRING")[1]
    else:
        value = evaluar_expresion_prefija(recorrer_preorden(parse_expression())) # !!!
    match("SEMICOLON")
    tabla_simbolos[name] = {
        "tipo" : var_type,
        "valor" : value
    }

# Gramatica play(myNote, duration);
def parse_play():
    match("PLAY")
    if current_token()[0] == "IDENTIFIER":
        match("IDENTIFIER")[1] 
    elif current_token()[0] == "STRING":
        match("STRING")[1]
    else:
        raise SyntaxError(f"Error de sintaxis, se esperaba play(string, numero)")
    match("COMMA")
    if current_token()[0] == "IDENTIFIER":
        match("IDENTIFIER")[1] 
    elif current_token()[0] == "NUMBER":
        match("NUMBER")[1]
    else:
        raise SyntaxError(f"Error de sintaxis, se esperaba play(string, numero)")
    match("RPAREN")
    match("SEMICOLON")

# Gramatica set_tempo(new_tempo);
def parse_set_tempo():    
    match("SET_TEMPO")
    if current_token()[0] == "IDENTIFIER":
        match("IDENTIFIER")[1] 
    elif current_token()[0] == "NUMBER":
        match("NUMBER")[1]
    else:
        raise SyntaxError(f"Error de sintaxis, se esperaba set_tempo(numero)")
    match("RPAREN")
    match("SEMICOLON")

# Regla para analizar un expresion aritmetica o logica <----- Agregar el arbol semantico
def parse_expression():
    left = parse_term()  # Parse el primer término
    
    while current_token()[0] in ("PLUS", "MINUS", "GREATER_THAN", "LESS_THAN", "GREATER_EQUAL", "LESS_EQUAL", "EQUALS", "NOT_EQUAL"):  # O bien operador aritmético o lógico
        operator = match(current_token()[0])[1]   # Consume el operador
        right = parse_term()  # Parse el siguiente término

    # Construir un nodo simplificado
        left = [operator, left, right]

    return left

# Regla para analizar un término (factores con * o /).
def parse_term():
    left = parse_factor()

    # Luego puede haber una secuencia de términos con operadores * o /
    while current_token() and current_token()[0] in ("MULT", "DIV_OP"):
        operator = match(current_token()[0])  # Consume el operador
        right = parse_factor()  # Analizamos el siguiente factor

        # Construir un nodo simplificado
        left = [operator, left, right]

    return left  # Retorna el nodo simplificado para el término

# Regla para analizar un factor (identificador, número, string o expresión entre paréntesis).
def parse_factor():
    left = current_token()
    
    if left[0] == "IDENTIFIER":
        #Analisis semantico validacion en la tabla de simbolos
        if not esta_declarada(left[1]):
            raise NameError(f"La variable '{left[1]}' no ha sido declarada antes de su uso. pos {current_pos}") 
        match("IDENTIFIER") 
        # Retorna el valor del identificador directamente
        return tabla_simbolos[left[1]]["valor"]

    elif left[0] == "NUMBER":
        value = float(match("NUMBER")[1])  # Consume el número y convierte a flotante
        return value  # Retorna directamente el valor
    
    elif left[0] == "STRING":
        value = match("STRING")[1]  # Consume la cadena
        return value  # Retorna directamente el valor
    
    elif left[0] == "LPAREN":
        match("LPAREN")  # Consume el paréntesis izquierdo
        expr = parse_expression()  # Analizamos la expresión entre paréntesis
        match("RPAREN")  # Consume el paréntesis derecho
        return expr
    else:
        raise SyntaxError(f"Se esperaba un identificador, número, cadena o '(', pero se encontró {left} en la posición {current_pos}")

def parse_if():
    """Regla para analizar un if."""
    match("IF")
    match("LPAREN")
    condition = evaluar_expresion_prefija(recorrer_preorden(parse_expression()))  # Analiza la condición correctamente
    match("RPAREN")
    match("LBRACE")
    body = parse_statements()
    match("RBRACE")
    
    else_body = None
    if current_token()[0] == "ELSE":
        match("ELSE")
        match("LBRACE")
        else_body = parse_statements()
        match("RBRACE")
    
# Regla para analizar un ciclo for.
def parse_for():
    match("FOR")
    match("LPAREN")
    
    # Declaración o asignación inicial
    initializer = None
    if current_token()[0] == "TYPE":  # Declaración de variable
        initializer = parse_var_decl()
        tabla_simbolos.append(initializer)
    elif current_token()[0] == "IDENTIFIER":  # Asignación a una variable existente
        initializer = parse_assignment_or_call()
    
    # Condición del ciclo
    condition = evaluar_expresion_prefija(recorrer_preorden(parse_expression()))
    match("SEMICOLON")
    
    # Actualización
    update = parse_assignment_or_call()
    match("RPAREN")
    
    # Cuerpo del ciclo
    match("LBRACE")
    body = parse_statements()
    match("RBRACE")

    # eliminar la variable temporal del for (i)
    # del tabla_simbolos[i]

# Regla para analizar un ciclo while.
def parse_while():
    match("WHILE")
    match("LPAREN")
    condition = parse_expression()  # Analiza la condición correctamente
    match("RPAREN")
    match("LBRACE")
    body = parse_statements()
    match("RBRACE")

# Regla para la asignacion de un valor a una variable o llamada a una funcion. 
def parse_assignment_or_call():
    name = match("IDENTIFIER")[1] 
    #Analisis semantico validacion en la tabla de simbolos
    if not esta_declarada(name):
        raise NameError(f"La variable '{name}' no ha sido declarada antes de su uso. pos {current_pos}")
    #Asignar un nuevo valor a una var
    if current_token()[0] == "ASSIGN":
        match("ASSIGN")
        value = evaluar_expresion_prefija(recorrer_preorden(parse_expression)) # !!!!
        match("SEMICOLON")
        tabla_simbolos[name]["valor"] = value
    #Llamada a una funcion
    elif current_token()[0] == "LPAREN":
        match("LPAREN")
        parse_arguments(name) # !!!!!!!
        match("RPAREN")
        match("SEMICOLON")
    # i++
    elif current_token()[0] == "PLUS":
        match("PLUS")
        if current_token()[0] == "PLUS":
            match("PLUS")
            tabla_simbolos[name]["value"] += 1   
    raise SyntaxError(f"Error en asignación o llamada: {name} en la posicion {current_pos}")


# Para en analisis semántico:
def esta_declarada(variable):
    return any(variable in entry for entry in tabla_simbolos)

#Analisis semantico: 
def recorrer_preorden(nodo):
    if isinstance(nodo, list):
        # Nodo interno (operador)
        operador = nodo[0]
        izquierdo = recorrer_preorden(nodo[1])
        derecho = recorrer_preorden(nodo[2])
        return f"{operador} {izquierdo} {derecho}"
    else:
        # Nodo hoja (literal o valor de un identificador)
        return str(nodo)

def evaluar_expresion_prefija(prefija):
    pila = []  # Pila para realizar los cálculos

    # Recorremos la expresión en orden inverso (de derecha a izquierda)
    for token in reversed(prefija.split()):
        if token.lstrip('-').replace('.', '').isdigit():  # Verifica si es un número
            pila.append(float(token))  # Convertimos a número y lo empujamos a la pila
        elif token in {"+", "-", "*", "/", ">", "<", ">=", "<=", "==", "!="}:
            # Sacamos los dos operandos de la pila
            operando1 = pila.pop()
            operando2 = pila.pop()

            # Realizamos la operación correspondiente
            if token == "+":
                pila.append(operando1 + operando2)
            elif token == "-":
                pila.append(operando1 - operando2)
            elif token == "*":
                pila.append(operando1 * operando2)
            elif token == "/":
                pila.append(operando1 / operando2)
            elif token == ">":
                pila.append(1.0 if operando1 > operando2 else 0.0)
            elif token == "<":
                pila.append(1.0 if operando1 < operando2 else 0.0)
            elif token == ">=":
                pila.append(1.0 if operando1 >= operando2 else 0.0)
            elif token == "<=":
                pila.append(1.0 if operando1 <= operando2 else 0.0)
            elif token == "==":
                pila.append(1.0 if operando1 == operando2 else 0.0)
            elif token == "!=":
                pila.append(1.0 if operando1 != operando2 else 0.0)
        else:
            raise ValueError(f"Símbolo no reconocido: {token} en la posicion {current_pos}")

    # El resultado final estará en la cima de la pila
    return pila.pop()


code = """
//Definicion de una funcion del usuario
void play_chord(int);

main(){
    // Declaracion de varibles
    int tempo = 120; // Tempo inicial
    note myNote = "C4"; // Nota inicial
    time duration = 6.0; //Duracion en beats

    //Asignacion de expresiones aritmeticas
    int new_tempo = tempo + 20;
}

// Declaracion de una funcion definida por el usuario
void play_chord(int duration){
    play("C4", duration);
    play("E4", duration);
    play("G4", duration);
}

"""

# Tokenizar el código
tokens = tokenize(code)
i = -1

print("\n\t- - - - - ANALIZADOR LÉXICO - - - - -")
print("\t\tTIPO TOKEN\t\tTOKEN")
for t in tokens:
    i += 1
    print(f"\t{i}\t{t[0].ljust(12)}\t\t{t[1]}")

# Reiniciar posición global
current_pos = 0

# Analizar el programa
print("\n\t- - - - - ANALIZADOR SINTÁCTICO - - - - -")
parse_program()
for simb in tabla_simbolos:
    print(f"\t{simb.ljust(10)}\t{tabla_simbolos[simb]}")
