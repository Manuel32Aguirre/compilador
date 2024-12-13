import re

def tokenize(code):
    # Expresión regular para dividir el código en tokens, ignorando comentarios
    token_specification = [
        ('NUMBER', r'\d+\.\d+|\d+'),   # Números
        ('ASSIGN', r'='),               # Asignación
        ('IDENTIFIER', r'[A-Za-z_][A-Za-z0-9_]*'),  # Identificadores
        ('TYPE', r'int|note|time'),     # Tipos de datos
        ('LPAREN', r'\('),              # Paréntesis izquierdo
        ('RPAREN', r'\)'),              # Paréntesis derecho
        ('LBRACE', r'\{'),              # Llave izquierda
        ('RBRACE', r'\}'),              # Llave derecha
        ('SEMICOLON', r';'),            # Punto y coma
        ('COMMA', r','),                # Coma
        ('DIV', r'//'),                 # Comentarios
        ('PLUS', r'\+'),                # Suma
        ('MINUS', r'-'),                # Resta
        ('MULT', r'\*'),                # Multiplicación
        ('DIV_OP', r'/'),               # División
        ('GREATER_THAN', r'>'),         # Mayor que
        ('LESS_THAN', r'<'),            # Menor que
        ('GREATER_EQUAL', r'>='),       # Mayor o igual
        ('LESS_EQUAL', r'<='),          # Menor o igual
        ('EQUALS', r'=='),              # Igual a
        ('NOT_EQUAL', r'!='),           # No igual
        ('IF', r'if'),                  # if
        ('ELSE', r'else'),              # else
        ('FOR', r'for'),                # for
        ('WHILE', r'while'),            # while
        ('STRING', r'"[^"]*"'),         # Cadenas entre comillas
        ('SKIP', r'[ \t\n]+'),          # Espacios en blanco y saltos de línea
        ('MISMATCH', r'.'),             # Cualquier otro carácter no esperado
    ]

    tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
    line_num = 1
    line_start = 0
    result = []
    
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP':  # Ignorar espacios en blanco y saltos de línea
            continue
        elif kind == 'DIV':  # Ignorar los comentarios
            continue
        elif kind == 'MISMATCH':  # Errores de sintaxis
            raise RuntimeError(f'{value!r} inesperado en la línea {line_num}')
        result.append((kind, value))
    return result
print(tokenize("int x = 10;"))