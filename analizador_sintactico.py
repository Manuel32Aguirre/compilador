""" from analizador_lexico import tokenize, errores_lex, error_lex
 """# Variables globales para el parser

current_pos = 0
tokens = []
tabla_simbolos = {}
errores_sint = []
error_sint = 0

# Devuelve una tupla (token actual, gramatica) o None si se han procesado todos los tokens.
def current_token():
    print(f"Estamos en current_token en la pos {current_pos}")
    return tokens[current_pos] if current_pos < len(tokens) else None

# Verifica si el token en la posicion actual y el esperado hacen match, si si consume un token esperado y devuelve la tupla (token actual, gramatica).
def match(expected_type):
    global current_pos, error_sint, errores_sint # "global" permite modificar la vairable global current_pos
    print(f"Estamos en match en la pos {current_pos}")
    token = current_token()
    if token and token[0] == expected_type:
        current_pos += 1
        return token
    print(f"hay un token que no coincide {token}")
    error_sint = 1
    errores_sint.append(("Error sintáctico", f"Se esperaba {expected_type}, pero se encontró {token} en la posicion {current_pos}"))
    return ("ERROR", token[1])


# Regla de producción inicial de la gramatica: programa completo.
def parse_program(contenido):
    global tokens, tabla_simbolos, current_pos
    print(f"Estamos en parse_program en la pos {current_pos}")
    tokens = contenido
    current_pos = 0
    tabla_simbolos["main"] = {
        "argumentos": []
    }
     # Leer prototipos de funciones
    while current_token() and current_token()[1] != "main": 
        parse_function_prot()
    # Leer funciones
    while current_token():  
        parse_func()

    return error_sint, errores_sint

# Regla para prototipos de funciones.
def parse_function_prot():
    global tabla_simbolos
    print(f"Estamos en parse_func_prot en la pos {current_pos}")
    func_type = match("TYPE")[1]
    name = match("IDENTIFIER")[1]  # Nombre de la función
    match("LPAREN")
    args = parse_function_args_prot()  # Procesar los argumentos
    match("RPAREN")
    match("SEMICOLON")
    tabla_simbolos[name] = {
        "argumentos" : args,
        "tipo" : func_type
    }

# Regla para procesar los ARGUMENTOS del PROTOTIPO de una funcion. (tipo identif o solo tipo). Devuelve una tupla(tipo, nombre)
def parse_function_args_prot():
    print("Estamos en parse_function_args_prot")
    args = []
    if current_token()[0] == "RPAREN":  # Sin argumentos
        return args
    while current_token() and current_token()[0] != "RPAREN":
        arg_type = match("TYPE")[1]  # Tipo de dato
        if current_token()[0] == "IDENTIFIER":  # Nombre del argumento (opcional)
            arg_name = match("IDENTIFIER")[1]
            args.append(((arg_type, arg_name)))
        else:  # Argumento solo con tipo
            args.append(((arg_type, "")))

        if current_token()[0] == "COMMA":  # Más argumentos
            match("COMMA")
        else:
            break
    return args

# Regla para procesar los ARGUMENTOS de la LLAMADA a una función. (forzosamente solo el nombre del parametro)
def parse_call_function_args(func):
    global error_sint, errores_sint
    if current_token()[0] == "RPAREN":  # Sin argumentos
        if(len(tabla_simbolos[func]["argumentos"]) != 0):
            error_sint = 1
            errores_sint.append(("Error semántico", f"En la llamada a la funcion: {func} en la pos: {current_pos}.\n\t\tEl prototipo indica que {func} recibe {len(tabla_simbolos[func]["argumentos"])} argumentos, pero no se esta mandando ningun argumento en esta llamada."))
        return
    i = 0
    while current_token() and current_token()[0] != "RPAREN":
        var = match("IDENTIFIER")[1] #identificador del argumento
        # validar que el tipo de la variable pasada por argumento coincida con el prototipo de la funcion y que la var exista en la tabla de simbolos
        if(esta_declarada(var)):
            if(i >= len(tabla_simbolos[func]["argumentos"])): 
                error_sint = 1
                print("si hay un error")
                errores_sint.append(("Error semántico", f"En la llamada a la funcion: {func} en la pos: {current_pos}.\n\t\tEl prototipo indica que {func} recibe {len(tabla_simbolos[func]["argumentos"])} argumentos, pero se estan mandando {i+1} argumentos en esta llamada."))
                break         
            if(tabla_simbolos[var]["tipo"] == tabla_simbolos[func]["argumentos"][i][0]):
                if current_token()[0] == "COMMA":  # Más argumentos
                    match("COMMA")
                    i+=1
                else:
                    i+=1
                    if(i != len(tabla_simbolos[func]["argumentos"])):
                        error_sint = 1
                        errores_sint.append(("Error semántico", f"En la llamada a la funcion: {func} en la pos: {current_pos}.\n\t\tEl prototipo indica que {func} recibe {len(tabla_simbolos[func]["argumentos"])} argumentos, pero se estan mandando {i} argumentos en esta llamada."))
                    break
            else:
                error_sint = 1
                errores_sint.append(("Error semántico", f"En la llamada a la funcion: {func} en la pos: {current_pos}.\n\t\tEl prototipo indica que {func}({tabla_simbolos[func]["argumentos"][i][0]}) pero la variable \"{var}\" es de tipo: {tabla_simbolos[var]["tipo"]}"))
        else: 
            error_sint = 1
            errores_sint.append(("Error semántico", f"En la llamada a la funcion: {func} en la pos: {current_pos}.\n\t\t\"La variable\" {var} no ha sido declarada."))
    print(error_sint)
    return 

# Regla para procesar los ARGUMENTOS del CUERPO de una funcion (forzosamente tipo e identif)
def parse_arguments_body_func(func):
    global error_sint, errores_sint, tabla_simbolos
    if current_token()[0] == "RPAREN":  # Sin argumentos
        return
    i = 0
    while current_token() and current_token()[0] != "RPAREN":
        # estas son variables temporales dentro de la funcion
        tipo = match("TYPE")[1]  # Tipo de dato
        var = match("IDENTIFIER")[1]

        if(i < len(tabla_simbolos[func]["argumentos"]) and tabla_simbolos[func]["argumentos"][i][0] == tipo):
            tabla_simbolos[var] = { # No esta validado usar el mismo nombre para una var en una funcion y en otra (variables temporales) 
                "tipo" : tipo,
                "valor" : 0 # falta asignar el valor pasado por parametro (ejecución)
            }
            tabla_simbolos[func]["argumentos"][i] = (tipo, var)  # Agrega el nombre a los argumentos de una funcion
        else:
            error_sint = 1
            errores_sint.append(("Error semántico", f"En la llamada a la funcion: {func} en la pos: {current_pos}.\n\t\tEl prototipo indica que \"{func}\" recibe {tabla_simbolos[func]["argumentos"][0][0]}."))
        
        if current_token()[0] == "COMMA":  # Más argumentos
            match("COMMA")
            i+=1
        else:
            break
    return 

# Regla de produccion para una funcion nombre(){...}
def parse_func():
    print("Estamos en parse_func")
    if current_token()[1] != "main":
        match("TYPE")[1]
    name = match("IDENTIFIER")[1]
    match("LPAREN")
    parse_arguments_body_func(name)
    match("RPAREN")
    match("LBRACE")
    parse_statements()
    match("RBRACE")

# Regla para argumentos de función.
def parse_arguments(func):
    global error_sint, errores_sint
    args = parse_call_function_args(func)
    i = 0
    if len(args) == len(tabla_simbolos[func]["argumentos"]):
        for a in args:
            if a[0] == tabla_simbolos[func]["argumentos"][i][0]:
                i+=1
            else: 
                error_sint = 1
                errores_sint.append(("Error semántico", f"en asignación o llamada: {func} en la posicion {current_pos}.\nSe esperaba{func}{tabla_simbolos[func]["argumentos"][0][0]}"))
        return
    else: 
        error_sint = 1
        errores_sint.append(("Error semántico", f"en asignación o llamada: {func} en la posicion {current_pos}.\nSe esperaba{func}{tabla_simbolos[func]["argumentos"][0][0]}"))

# Regla para cada instrucción de una funcion
print("Estamos en parse_statements")
def parse_statements():
    while current_token() and current_token()[0] != "RBRACE": # mientras haya tokens por consumir y no se trate de '}' #¿Esto funciona para for(){expresiones}
        parse_statement()

# Clasifica si una instrucciones es una declaracion de variable, una asignación, una llamada a una funcion o una estructura if, for o while
def parse_statement():
    global error_sint, errores_sint
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
        error_sint = 1
        errores_sint.append(("Error sintáctico", f"Sentencia no válida: {token} posicion {current_pos}"))

# Regla para declaración de variables. 
def parse_var_decl():
    global tabla_simbolos
    var_type = match("TYPE")[1]
    name = match("IDENTIFIER")[1]
    match("ASSIGN")
    if current_token()[0] == "STRING":
        value = match("STRING")[1]
    else:
        value = evaluar_expresion_prefija(recorrer_preorden(parse_expression()))
    match("SEMICOLON")
    tabla_simbolos[name] = {
        "tipo" : var_type,
        "valor" : value
    }

# Gramatica play(myNote, duration);
def parse_play():
    global error_sint, errores_sint
    match("PLAY")
    if current_token()[0] == "IDENTIFIER":
        match("IDENTIFIER")[1] 
    elif current_token()[0] == "STRING":
        match("STRING")[1]
    else:
        error_sint = 1
        errores_sint.append(("Error sintáctico", f"Se esperaba play(string, numero)"))
    match("COMMA")
    if current_token()[0] == "IDENTIFIER":
        match("IDENTIFIER")[1] 
    elif current_token()[0] == "NUMBER":
        match("NUMBER")[1]
    else:
        error_sint = 1
        errores_sint.append(("Error sintáctico", f"Se esperaba play(string, numero)"))
    match("RPAREN")
    match("SEMICOLON")

# Gramatica set_tempo(new_tempo);
def parse_set_tempo():
    global error_sint, errores_sint
    match("SET_TEMPO")
    if current_token()[0] == "IDENTIFIER":
        match("IDENTIFIER")[1] 
    elif current_token()[0] == "NUMBER":
        match("NUMBER")[1]
    else:
        error_sint = 1
        errores_sint.append(("Error sintáctico", f"Se esperaba set_tempo(numero)"))
    match("RPAREN")
    match("SEMICOLON")

def parse_if():
    print("Estamos en parse_if")
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
    print("Estamos en parse_for")
    match("FOR")
    match("LPAREN")
    
    # Declaración o asignación inicial
    if current_token()[0] == "TYPE":  # Declaración de variable
        parse_var_decl()
    elif current_token()[0] == "IDENTIFIER":  # Asignación a una variable existente
        parse_assignment_or_call()
    
    # Condición del ciclo
    evaluar_expresion_prefija(recorrer_preorden(parse_expression()))
    match("SEMICOLON")
    
    # Actualización
    parse_assignment_or_call()
    match("RPAREN")
    
    # Cuerpo del ciclo
    match("LBRACE")
    parse_statements()
    match("RBRACE")

    # eliminar la variable temporal del for (i)
    # del tabla_simbolos[i]

# Regla para analizar un ciclo while.
def parse_while():
    print("Estamos en parse_while")
    match("WHILE")
    match("LPAREN")
    condition = parse_expression()  # Analiza la condición correctamente
    match("RPAREN")
    match("LBRACE")
    body = parse_statements()
    match("RBRACE")

# Regla para (asignacion de un valor a una variable) o (llamada a una funcion). 
def parse_assignment_or_call():
    global error_sint, errores_sint, tabla_simbolos
    name = match("IDENTIFIER")[1] 
    #Analisis semantico validacion en la tabla de simbolos
    if not esta_declarada(name):
        error_sint = 1
        errores_sint.append("Error semántico", f"La variable \"{name}\"' no ha sido declarada antes de su uso. En la pos {current_pos}")
    
    #Asignar un nuevo valor a una var
    if current_token()[0] == "ASSIGN":
        global tabla_simbolos
        match("ASSIGN")
        value = evaluar_expresion_prefija(recorrer_preorden(parse_expression())) 
        match("SEMICOLON")
        tabla_simbolos[name]["valor"] = value
    
    #Llamada a una funcion
    elif current_token()[0] == "LPAREN":
        match("LPAREN")
        parse_call_function_args(name) 
        match("RPAREN")
        match("SEMICOLON")
    
    # i++
    elif current_token()[0] == "PLUS":
        match("PLUS")
        if current_token()[0] == "PLUS":
            match("PLUS")
            tabla_simbolos[name]["valor"] += 1   
    
    else:
        error_sint = 1
        errores_sint.append("Error sintáctico", f"No se ha reconocido la asignación o llamada a la {name} en la posicion {current_pos}")

#Analisis semantico: 

def esta_declarada(variable):
    return any(variable in entry for entry in tabla_simbolos)

# Regla para analizar un expresion aritmetica o logica <----- Agregar el arbol semantico
def parse_expression():
    print("Estamos en parse_expression")
    left = parse_term()  # Parse el primer término
    while current_token()[0] in ("PLUS", "MINUS", "GREATER_THAN", "LESS_THAN", "GREATER_EQUAL", "LESS_EQUAL", "EQUALS", "NOT_EQUAL"):  # O bien operador aritmético o lógico
        operator = current_token()[1]
        match(current_token()[0])   # Consume el operador
        right = parse_expression()  # Parse el siguiente término
        # Construir un nodo simplificado
        left = [operator, left, right]

    return left

# Regla para analizar un término (factores con * o /).
def parse_term():
    print("Estamos en parse_term")
    left = parse_factor()
    # Luego puede haber una secuencia de términos con operadores * o /
    while current_token() and current_token()[0] in ("MULT", "DIV_OP"):
        operator = current_token()[1]  # Consume el operador
        match(current_token()[0])
        right = parse_factor()  # Analizamos el siguiente factor

        # Construir un nodo simplificado
        left = [operator, left, right]

    return left  # Retorna el nodo simplificado para el término

# Regla para analizar un factor (identificador, número, string o expresión entre paréntesis).
def parse_factor():
    global error_sint, errores_sint
    print("Estamos en parse_factor")
    global error
    left = current_token()

    # Retorna el valor del identificador directamente
    if left[0] == "IDENTIFIER":
        #Analisis semantico validacion en la tabla de simbolos
        if not esta_declarada(left[1]):
            error_sint = 1
            errores_sint.append("Error semántico", f"La variable \"{left[1]}\" no ha sido declarada antes de su uso. pos {current_pos}")
        match("IDENTIFIER") 
        return tabla_simbolos[left[1]]["valor"]

    # Retorna directamente el numero
    elif left[0] == "NUMBER":
        value = float(match("NUMBER")[1])  # Consume el número y convierte a flotante
        return value  
    
    # Retorna directamente el string
    elif left[0] == "STRING":
        value = match("STRING")[1]  # Consume la cadena
        return value  
    
    # Consume ( manda a llamar a parse_expression() )
    elif left[0] == "LPAREN":
        match("LPAREN")  # Consume el paréntesis izquierdo
        expr = parse_expression()  # Analizamos la expresión entre paréntesis
        match("RPAREN")  # Consume el paréntesis derecho
        return expr
    
    else:
        error=1
        errores_sint.append("Error sintáctico y semántico", f"Se esperaba un identificador, número, cadena o '(', pero se encontró {left} en la posición {current_pos}")

def recorrer_preorden(nodo):
    print("Estamos en recorrer_preorden")
    if isinstance(nodo, list):
        # Nodo interno (operador)
        operador = nodo[0]
        izquierdo = recorrer_preorden(nodo[1]) #si es un arbol nodo[1] será otra lista
        derecho = recorrer_preorden(nodo[2])
        return f"{operador} {izquierdo} {derecho}"
    else:
        # Nodo hoja (literal o valor de un identificador)
        return str(nodo)

def evaluar_expresion_prefija(prefija):
    global error_sint, errores_sint
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
            error_sint = 1
            errores_sint.append("Error léxico", f"Símbolo no reconocido: {token} en la posicion {current_pos}")

    # El resultado final estará en la cima de la pila
    return pila.pop()



"""

//Definicion de una funcion del usuario
void play_chord(time);

main(){
    // Declaracion de varibles
    int tempo = 120; // Tempo inicial
    note myNote = "C4"; // Nota inicial
    time duration = 6.0; //Duracion en beats

    //Asignacion de expresiones aritmeticas
    int new_tempo = tempo + 20;
    duration = duration/2+1;

    //Llamada a funciones predefinidas
    set_tempo(new_tempo); // Ajusta el tempo a 140 BPM
    play(myNote, duration); // Reproduce la nota C4 durante 1 beat

    //Estructura de control if-else
    if(new_tempo > 130){
        play("E4", 0.5); // Nota E4 si el tempo supera 130 BPM
    }
    else{
        play("G4", 0.5); // Nota G4 en caso contrario
    }
    //Ciclo for
    for(int i=0; i<4; i++){
        play("A4", 0.25); // Reproduce A4 cuatro veces durante 0.25 beats
    }

    play_chord(duration); // Llama a la funcion para reproducir una acorde

    //Ciclo while
    int count = 3;
    while(count > 0){
        play("B4", 0.5); // Reproduce B4 tres veces
        count = count - 1;
    }
}

// Declaracion de una funcion definida por el usuario
void play_chord(time dur){
    play("C4", dur);
    play("E4", dur);
    play("G4", dur);
}



# Tokenizar el código
tokens = tokenize(code)
i = -1

print("\n\t- - - - - ANALIZADOR LÉXICO - - - - -")
if(error_lex == 1):
    print("\n\tEl código presenta errores léxicos:")
    for e in errores_lex:
        print(f"\t{e[0]}\n\t\t{e[1]}")

print("\t\tTIPO TOKEN\t\tTOKEN")
for t in tokens:
    i += 1
    print(f"\t{i}\t{t[0].ljust(12)}\t\t{t[1]}")

# Reiniciar posición global
current_pos = 0

# Analizar el programa
print("\n\t- - - - - ANALIZADOR SINTÁCTICO - - - - -")
parse_program()
if(error == 1):
    print("\n\tEl código presenta errores:")
    for e in errores:
        print(f"\t{e[0]}\n\t\t{e[1]}")
print("\n\tTabla de símbolos de las funciones y variables del código:")
for simb in tabla_simbolos:
    print(f"\t{simb.ljust(10)}\t{tabla_simbolos[simb]}")"""