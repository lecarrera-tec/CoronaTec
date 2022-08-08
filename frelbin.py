from typing import List, Tuple
Matriz = List[List[int]]

def grafico2grafico(G: List[tuple], A: List[str], B: List[str] = []):
    """ Construye un grafico a partir de una grafico y el conjunto
    de llegada (y el de salida en caso de que fueran distintos). """
    resp = []
    if not B:
        B = A
    for i,j in G:
        resp.append((A[i], B[j]))
    resp = str(resp)
    resp = resp.replace('[]', r'\varnothing').replace("'", '')
    resp = resp.replace('[', r'\{').replace(']', r'\}')
    return resp

def grafico2matriz(G : List[tuple], nfilas: int, ncols: int = 0):
    if not ncols:
        ncols = nfilas
    resp = []
    for i in range(nfilas):
        resp.append([0] * ncols)
    for i,j in G:
        resp[i][j] = 1
    return resp

def matriz2grafico(M: Matriz, A: List[str] = [], B: List[str] = []):
    """ Construye un grafico a partir de una matriz y el conjunto
    de llegada (y el de salida en caso de que fueran distintos). """
    nfilas = len(M)
    assert(nfilas > 0)
    ncols  = len(M[0])
    resp = []
    if A:
        if not B:
            B = A
        assert(nfilas == len(A))
        assert(ncols  == len(B))
        for i in range(nfilas):
            for j in range(ncols):
                if M[i][j]:
                    resp.append((A[i], B[j]))
        resp = str(resp)
        resp = resp.replace('[]', r'\varnothing').replace("'", '')
        resp = resp.replace('[', r'\{').replace(']', r'\}')
    else:
        for i in range(nfilas):
            for j in range(ncols):
                if M[i][j]:
                    resp.append((i, j))
    return resp

def esMatrizReflexiva(M):
    nfilas = len(M)
    assert(nfilas > 0)
    ncols = len(M[0])
    if nfilas is not ncols:
        return False
    for i in range(nfilas):
        if not M[i][i]:
            return False
    return True

def esMatrizSimetrica(M):
    nfilas = len(M)
    assert(nfilas > 0)
    ncols = len(M[0])
    if nfilas is not ncols:
        return False
    for i in range(nfilas):
        for j in range(i):
            if M[i][j] is not M[j][i]:
                return False
    return True

def esMatrizTransitiva(M: Matriz):
    nfilas = len(M)
    assert(nfilas > 0)
    ncols = len(M[0])
    if nfilas is not ncols:
        return False
    T = matricesComp(M, M)
    return esMatricesMenorIgual(T, M)

def esMatrizAntisimetrica(M: Matriz):
    nfilas = len(M)
    assert(nfilas > 0)
    if nfilas is not len(M[0]):
        return False
    for i in range(nfilas):
        for j in range(i):
            if M[i][j] and M[j][i]:
                return False
    return True

def esMatrizTotal(M: Matriz):
    nfilas = len(M)
    assert(nfilas > 0)
    if nfilas is not len(M[0]):
        return False
    for i in range(nfilas):
        if not M[i][i]:
            return False
        for j in range(i):
            if not M[i][j] and not M[j][i]:
                return False
    return True

def esMatricesMenorIgual(M1: Matriz, M2: Matriz):
    nfilas = len(M1)
    assert(nfilas > 0)
    ncols = len(M1[0])
    assert(nfilas == len(M2))
    assert(ncols == len(M2[0]))
    for i in range(nfilas):
        for j in range(ncols):
            if M1[i][j]:
                if not M2[i][j]:
                    return False
    return True

def matrizDominio(M: Matriz, A=str):
    nfilas = len(M)
    resp = [0] * nfilas
    for i in range(nfilas):
        if sum(M[i]):
            resp[i] = 1
    resp = [A[i] for i in range(nfilas) if resp[i]]
    return resp

def matrizAmbito(M: Matriz, B=str):
    return matrizDominio(matrizTranspuesta(M), B)

def matrizNegar(M: Matriz):
    nfilas = len(M)
    assert(nfilas > 0)
    ncols = len(M[0])
    resp = []
    for i in range(nfilas):
        resp.append([1] * ncols)
        for j in range(ncols):
            if M[i][j]:
                resp[i][j] = 0
    return resp

def matricesAnd(M1: Matriz, M2: Matriz):
    nfilas = len(M1)
    assert(nfilas > 0)
    ncols = len(M1[0])
    assert(nfilas == len(M2))
    assert(ncols == len(M2[0]))
    resp = []
    for i in range(nfilas):
        resp.append([0] * ncols)
        for j in range(ncols):
            if M1[i][j] and M2[i][j]:
                resp[i][j] = 1
    return resp

def matricesOr(M1: Matriz, M2: Matriz):
    nfilas = len(M1)
    assert(nfilas > 0)
    ncols = len(M1[0])
    assert(nfilas == len(M2))
    assert(ncols == len(M2[0]))
    resp = []
    for i in range(nfilas):
        resp.append([0] * ncols)
        for j in range(ncols):
            if M1[i][j] or M2[i][j]:
                resp[i][j] = 1
    return resp

def matricesComp(M1: Matriz, M2: Matriz):
    nfilas = len(M1)
    assert(nfilas > 0)
    ncomun = len(M1[0])
    assert(ncomun > 0)
    assert(ncomun == len(M2))
    ncols = len(M2[0])
    resp = []
    for i in range(nfilas):
        resp.append([0] * ncols)
        for j in range(ncols):
            for k in range(ncomun):
                if M1[i][k] and M2[k][j]:
                    resp[i][j] = 1
                    break
    return resp

def matrizTranspuesta(M: Matriz):
    ncols = len(M)
    assert(ncols > 0)
    nfilas = len(M[0])
    resp = []
    for i in range(nfilas):
        resp.append([0] * ncols)
        for j in range(ncols):
            if M[j][i]:
                resp[i][j] = 1
    return resp

def reglaMatriz(nfilas: int, ncols: int, f):
    resp = []
    for i in range(nfilas):
        resp.append([0] * ncols)
        for j in range(ncols):
            if f(i, j):
                resp[i][j] = 1
    return resp

def reglaGrafico(A: list, B: list, f):
    nfilas = len(A)
    ncols = len(B)
    resp = []
    for i in range(nfilas):
        for j in range(ncols):
            if f(A[i], B[j]):
                resp.append((i,j))
    return resp
