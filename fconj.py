import itertools

def impComo(ls: list) -> str:
    """ Imprime una lista como conjunto. Intercambia cada '['
    por llaves. """
    texto = str(ls)
    texto = texto.replace('[]', r'\varnothing')
    texto = texto.replace('[', r'\{').replace(']', r'\}')
    return texto

def union(A, B):
    C = A[:]
    for b in B:
        if b not in C:
            C.append(b)
    return C

def interseccion(A, B):
    C = []
    for a in A:
        if a in B:
            C.append(a)
    return C

def diferencia(A, B):
    C = []
    for a in A:
        if a not in B:
            C.append(a)
    return C

def dsimetrica(A, B):
    C = diferencia(union(A,B), interseccion(A,B))
    return C

def potencia(A) -> list:
    """ Construye el conjunto potencia de A. A puede ser una lista. """
    n = len(A)
    ls = []
    for k in range(n+1):
        ls += [list(p) for p in itertools.combinations(A, k)]
    return ls

def producto(A, B) -> list:
    """ Construye el producto de A y B, que pueden ser listas. """
    return list(itertools.product(A, B))
