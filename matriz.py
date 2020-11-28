import random
from typing import List

from ftexto import minCifras
import vector as v


# Definición del tipo matriz.
Matriz = List[List[float]]


def aleatorio(nfilas: int, ncols: int, vmin: int, vmax: int,
              factor: float = 1) -> Matriz:
    """ Genera una matriz de números aleatorios.

    Argumentos
    ----------
    nfilas:
        Número de filas de la matriz.
    ncols:
        Número de columnas de la matriz.
    vmin:
        Mínimo valor entero a generar.
    vmax:
        Máximo valor entero a generar.
    factor:
        Opcional. Constante por la cual se multiplica la matriz.
        El valor predeterminado es 1.0
    """
    mat: Matriz = []
    mat = [[factor * random.randint(vmin, vmax) for j in range(ncols)]
           for i in range(nfilas)]
    return mat


def copia(A: Matriz) -> Matriz:
    """ Devuelve una copia de la matriz. """
    B: Matriz = []
    for fila in A:
        B.append(fila.copy())
    return B


def cambiar(A: Matriz, irow: int, icol: int, valor: float) -> Matriz:
    """ Se actualiza el valor de la matriz. """
    B = copia(A)
    B[irow][icol] = valor
    return B


def dominante(n: int, vmin: int, vmax: int, factor: float = 1) -> Matriz:
    """ Construye una matriz cuadrada diagonalmente dominante.

    Argumentos
    ----------
    n:
        Tamaño de la matriz.
    vmin:
        Mínimo valor entero a generar.
    vmax:
        Máximo valor entero a generar.
    factor:
        Opcional. Constante por la cual se multiplica el vector.
        El valor predeterminado es 1.0
    """
    mat: Matriz = []
    fila: List[int]
    for i in range(n):
        fila = [random.randint(vmin, vmax) for j in range(n)]
        fila[i] = random.randint(vmin, vmax - 1)
        # Se quita el 0 como posible valor
        if fila[i] >= 0:
            fila[i] += 1
            signo = 1
        else:
            fila[i] = abs(fila[i])
            signo = -1
        for j in range(n):
            if j == i:
                continue
            fila[i] += abs(fila[j])
        mat.append([factor * mij for mij in fila])
        mat[i][i] *= signo
    return mat


def latex(mat: Matriz, cifras: int = -1, ceros: int = 3) -> str:
    """ Imprime una matriz.

    Observe que solamente imprime el relleno. Es decir, se debe utilizar
    \\begin{pmatrix} ... \\end{pmatrix} o lo que se quiera ...

    Argumentos
    ----------
    mat:
        Matriz a imprimir.
    cifras:
        Opcional. Número de cifras a imprimir. El valor predeterminado
        es -1, que trata de ajustar al mínimo posible utilizando el
        valor de `ceros` para determinar dónde detenerse.
    ceros:
        Opcional. Se utiliza solo cuando cifras == -1. Número de ceros
        que hace que el resto de valores distintos de cero sean
        descartados.
    """
    matTexto: List[List[str]]
    if cifras == -1:
        matTexto = [[minCifras(elem, ceros) for elem in fila] for fila in mat]
    else:
        formato: str = '%%.%df' % cifras
        matTexto = [[formato % elem for elem in fila] for fila in mat]
    texto = '  %s' % ' \\\\\n  '.join([' & '.join(fila) for fila in matTexto])
    return texto


def jacobi(A: Matriz, bb: v.Vector, x0: v.Vector, npasos: int) -> v.Vector:
    """ Ejecuta n pasos del método de Jacobi, iniciando en x0.

    Argumentos
    ----------
    A:
        Matriz que se asume es diagonalmente dominante, ya ordenada.
    bb:
        Vector solución.
    x0:
        Aproximación inicial.
    npasos:
        Número de pasos.
    """
    nfilas: int = len(A)
    assert(nfilas > 0)
    ncols: int = len(A[0])
    assert(ncols == len(x0))
    xr: v.Vector = v.ceros(ncols)
    for k in range(npasos):
        for i in range(nfilas):
            xr[i] = (bb[i] - sum([A[i][j] * x0[j]
                                 for j in range(ncols) if j != i])) / A[i][i]
        x0 = xr.copy()
    return xr


def gaussSeidel(A: Matriz, bb: v.Vector, x0: v.Vector,
                npasos: int) -> v.Vector:
    """ Ejecuta n pasos del método de Gauss-Seidel, iniciando en x0.

    Argumentos
    ----------
    A:
        Matriz que se asume es diagonalmente dominante, ya ordenada.
    bb:
        Vector solución.
    x0:
        Aproximación inicial.
    npasos:
        Número de pasos.
    """
    nfilas: int = len(A)
    assert(nfilas > 0)
    ncols: int = len(A[0])
    assert(ncols == len(x0))
    xr: v.Vector = x0.copy()
    for k in range(npasos):
        for i in range(nfilas):
            xr[i] = (bb[i] - sum([A[i][j] * xr[j]
                                 for j in range(ncols) if j != i])) / A[i][i]
    return xr


def intercambiar(A: Matriz, fila1: int, fila2: int) -> Matriz:
    """ Intercambia dos filas de una matriz. """
    A[fila1], A[fila2] = A[fila2], A[fila1]
    return A


def permutar(A: Matriz, perm: List[int]) -> Matriz:
    """ Coloca los índices de las filas de A, según la permutación. """
    B = [A[j] for j in perm]
    return B


def sistema(A: Matriz, b: v.Vector) -> v.Vector:
    """ Resuelve Ax = b """
    A = copia(A)
    b = b.copy()
    n = len(A)
    xs = n * [0]
    assert(n > 0)
    assert(n == len(A[0]))
    for i in range(n - 1):
        _, ipiv = max([(abs(A[i+k][i]), i+k) for k in range(n - i)])
        if i != ipiv:
            A = intercambiar(A, i, ipiv)
            b[i], b[ipiv] = b[ipiv], b[i]
        for iFila in range(i + 1, n):
            if A[iFila][i] != 0.0:
                k = A[iFila][i] / A[i][i]
                A[iFila][i] = 0
                for iCol in range(i + 1, n):
                    A[iFila][iCol] -= k * A[i][iCol]
                b[iFila] -= k * b[i]
    for i in range(n-1,-1,-1):
        xs[i] = (b[i] - sum([A[i][j] * xs[j] for j in range(i+1, n)])) / A[i][i]
    return xs
