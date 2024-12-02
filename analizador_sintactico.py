from analizador_lexico import tokenize
# Variables globales para el parser
current_pos = 0
tokens = []

def current_token():
    """Devuelve el token actual o None si se han procesado todos."""
    global current_pos, tokens
    return tokens[current_pos] if current_pos < len(tokens) else None

def match(expected_type):
    """Verifica y consume un token esperado."""
    global current_pos
    token = current_token()
    if token and token[0] == expected_type:
        current_pos += 1
        return token
    raise SyntaxError(f"Se esperaba {expected_type}, pero se encontró {token}")

def parse_program():
    """Regla inicial: programa completo."""
    return parse_main()

def parse_main():
    """Regla para la función main()."""
    match("MAIN")  # Esto debe coincidir con la palabra clave 'main'
    match("LPAREN")
    match("RPAREN")
    match("LBRACE")
    statements = parse_statements()
    match("RBRACE")
    return {"type": "main", "body": statements}


def parse_statements():
    """Regla para múltiples sentencias."""
    statements = []
    while current_token() and current_token()[0] != "RBRACE":
        statements.append(parse_statement())
    return statements

def parse_statement():
    """Regla para una sentencia: declaración, asignación o control."""
    token = current_token()
    if token[0] == "TYPE":
        return parse_var_decl()
    elif token[0] == "IDENTIFIER":
        return parse_assignment_or_call()
    elif token[0] == "IF":
        return parse_if()
    elif token[0] == "FOR":
        return parse_for()
    elif token[0] == "WHILE":
        return parse_while()
    raise SyntaxError(f"Sentencia no válida: {token}")

def parse_var_decl():
    """Regla para declaración de variables."""
    var_type = match("TYPE")[1]
    name = match("IDENTIFIER")[1]
    match("ASSIGN")
    value = parse_expression()
    match("SEMICOLON")
    return {"type": "var_decl", "var_type": var_type, "name": name, "value": value}

def parse_assignment_or_call():
    """Regla para asignación o llamada a función."""
    name = match("IDENTIFIER")[1]
    if current_token()[0] == "ASSIGN":
        match("ASSIGN")
        value = parse_expression()
        match("SEMICOLON")
        return {"type": "assignment", "name": name, "value": value}
    elif current_token()[0] == "LPAREN":
        match("LPAREN")
        args = parse_arguments()
        match("RPAREN")
        match("SEMICOLON")
        return {"type": "function_call", "name": name, "args": args}
    raise SyntaxError(f"Error en asignación o llamada: {name}")

def parse_expression():
    """Regla para analizar una expresión."""
    left = current_token()
    if left[0] in ("IDENTIFIER", "NUMBER"):  # Identificadores o números
        match(left[0])
        if current_token()[0] in ("GREATER_THAN", "LESS_THAN", "GREATER_EQUAL", "LESS_EQUAL", "EQUALS", "NOT_EQUAL"):
            operator = current_token()
            match(operator[0])
            right = current_token()
            if right[0] in ("IDENTIFIER", "NUMBER"):  # Operando derecho
                match(right[0])
                return {
                    "type": "binary_expression",
                    "operator": operator[1],
                    "left": left[1],
                    "right": right[1]
                }
            else:
                raise SyntaxError(f"Se esperaba un identificador o número, pero se encontró {right}")
        else:
            return {"type": "literal", "value": left[1]}
    elif left[0] == "LPAREN":  # Expresiones con paréntesis
        match("LPAREN")
        expr = parse_expression()
        match("RPAREN")
        return expr
    else:
        raise SyntaxError(f"Se esperaba un identificador, número o '(', pero se encontró {left}")


def parse_arguments():
    """Regla para argumentos de función."""
    args = []
    while current_token() and current_token()[0] != "RPAREN":
        args.append(parse_expression())
        if current_token()[0] == "COMMA":
            match("COMMA")
    return args

def parse_if():
    """Regla para analizar un if."""
    match("IF")
    match("LPAREN")
    condition = parse_expression()  # Analiza la condición correctamente
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
    
    return {
        "type": "if",
        "condition": condition,
        "body": body,
        "else": else_body
    }


def parse_for():
    """Regla para analizar un ciclo for."""
    match("FOR")
    match("LPAREN")
    
    # Declaración o asignación inicial
    initializer = None
    if current_token()[0] == "TYPE":  # Declaración de variable
        initializer = parse_var_decl()
    elif current_token()[0] == "IDENTIFIER":  # Asignación a una variable existente
        initializer = parse_assignment_or_call()
    
    # Condición del ciclo
    condition = parse_expression()
    match("SEMICOLON")
    
    # Actualización
    update = parse_assignment_or_call()
    match("RPAREN")
    
    # Cuerpo del ciclo
    match("LBRACE")
    body = parse_statements()
    match("RBRACE")
    
    return {
        "type": "for",
        "initializer": initializer,
        "condition": condition,
        "update": update,
        "body": body
    }

def parse_while():
    """Regla para analizar un ciclo while."""
    match("WHILE")
    match("LPAREN")
    condition = parse_expression()  # Analiza la condición correctamente
    match("RPAREN")
    match("LBRACE")
    body = parse_statements()
    match("RBRACE")
    
    return {
        "type": "while",
        "condition": condition,
        "body": body
    }




code = """
// Definicion de una funcion del usuario
play_chord(int);

main() {
    // Declaracion de variables
    int tempo = 120;        // Tempo inicial
    note myNote= "C4";     // Nota inicial
    time duration = 6.0;   // Duracion en beats

    // Asignacion de expresiones aritmeticas
    int new_tempo = tempo + 20;
    duration=duration/2+1

    // Llamada a funciones predefinidas
    set_tempo(new_tempo);   // Ajusta el tempo a 140 BPM
    play(myNote, duration);   // Reproduce la nota C4 durante 1 beat

    // Estructura de control if-else
    if (new_tempo > 130) {
        play("E4", 0.5);    // Nota E4 si el tempo supera 130 BPM
    } else {
        play("G4", 0.5);    // Nota G4 en caso contrario
    }

    // Ciclo for
    for (int i = 0; i < 4; i++) {
        play("A4", 0.25);   // Reproduce A4 cuatro veces durante 0.25 beats
    }

    play_chord();           // Llama a la funcion para reproducir un acorde

    // Ciclo while
    int count = 3;
    while (count > 0) {
        play("B4", 0.5);    // Reproduce B4 tres veces
        count = count - 1;
    }
}

// Declaracion de una funcion definida por el usuario
    void play_chord() {
        play("C4", duration);
        play("E4", duration);
        play("G4", duration);
    }
"""

# Tokenizar el código
tokens = tokenize(code)
print(tokens)
# Reiniciar posición global
current_pos = 0

# Analizar el programa
ast = parse_program()
print(ast)
