from collections import defaultdict

# Función para cargar las producciones desde el archivo
def load_and_split_productions(filename):
    productions = defaultdict(list)
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            # Dividir el lado izquierdo y derecho de la producción
            head, body = line.strip().split('⟶')
            head = head.strip()
            # Dividir las alternativas por '|'
            alternatives = body.split('|')
            for alt in alternatives:
                productions[head].append(alt.strip())
    return productions

# Función para calcular el conjunto Primero
def compute_first(productions):
    first = defaultdict(set)

    # Función auxiliar para calcular Primero de un símbolo
    def compute_first_of(symbol):
        # Si el símbolo ya tiene su conjunto Primero calculado, regresar
        if symbol in first and first[symbol]:
            return first[symbol]
        
        # Si el símbolo es un terminal, su Primero es él mismo
        if not symbol.isupper():
            return {symbol}

        # Calcular Primero del no terminal
        for production in productions[symbol]:
            for char in production:
                # Obtener Primero del símbolo actual
                first_char = compute_first_of(char)
                first[symbol].update(first_char - {'ε'})
                
                # Si el símbolo no puede derivar ε, terminamos aquí
                if 'ε' not in first_char:
                    break
            else:
                # Si llegamos al final y todos los símbolos pueden derivar ε, agregamos ε
                first[symbol].add('ε')

        return first[symbol]

    # Calcular Primero para cada no terminal
    for non_terminal in productions:
        compute_first_of(non_terminal)

    return first

# Cargar las producciones desde el archivo
productions = load_and_split_productions('gramatica.txt')

# Calcular conjuntos Primero
first_sets = compute_first(productions)

# Imprimir las producciones separadas
print("Producciones:")
for head, alternatives in productions.items():
    for alt in alternatives:
        print(f"{head} ⟶ {alt}")

# Imprimir los conjuntos Primero
print("\nConjuntos Primero:")
for non_terminal, first_set in first_sets.items():
    print(f"Primero({non_terminal}) = {first_set}")
#