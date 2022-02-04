import random
from typing import List

from ftexto import minCifras
from ftexto import fraccion
from fractions import Fraction


# Definici\'on del tipo vector.
Vector = List[Fraction]


def ceros(n: int) -> Vector:
    """ Un vector de ceros de tamaño n. """
    return n * [Fraction(0,1)]


def aleatorio(n: int, vmin: int, vmax: int, factor: Fraction = Fraction(1,1)) -> Vector:
    """ Genera un vector de números aleatorios.

    Argumentos
    ----------
    n:
        Tamaño del vector.
    vmin:
        Mínimo valor entero a generar.
    vmax:
        Máximo valor entero a generar.
    factor:
        Opcional. Constante por la cual se multiplica el vector.
        El valor predeterminado es 1
    """
    return [factor * random.randint(vmin, vmax) for i in range(n)]


def latex(v: Vector, txtSep: str, cifras: int = -2, ceros: int = 3) -> str:
    """ Imprime un vector. El separador permite el formato.

    Observe que solamente imprime el relleno. Es decir, se debe utilizar
    \\begin{pmatrix} ... \\end{pmatrix} o lo que se quiera ...

    Argumentos
    ----------
    v:
        Vector a imprimir.
    txtSep:
        Texto de separador entre elementos. Para un vector fila puede
        utilizar ', ', o ' & '. Para un vector columna debería utilizar
        ' \\\\ '.
    cifras:
        Opcional. Número de cifras a imprimir. El valor predeterminado
        es -2, que imprime fracciones. El valor de -1 trata de ajustar 
        al mínimo posible utilizando el valor de `ceros` para determinar 
        dónde detenerse.
    ceros:
        Opcional. Se utiliza solo cuando cifras == -1. Número de ceros
        que hace que el resto de valores distintos de cero sean
        descartados.
    """
    vTexto: List[str]
    if cifras == -2:
        vTexto = [fraccion(elem.numerator, elem.denominator) for elem in v]
    elif cifras == -1:
        vTexto = [minCifras(elem, ceros) for elem in v]
    else:
        formato: str = '%%.%df' % cifras
        vTexto = [formato % elem for elem in v]
    return txtSep.join(vTexto)

def kprod(k: Fraction, v: Vector) -> Vector:
    return [k * vi for vi in v]

def pprod(u: Vector, v: Vector) -> Fraction:
    n = min(len(u), len(v))
    return sum([u[k] * v[k] for k in range(n)])

def suma(v1: Vector, v2: Vector) -> Vector:
    return [v1[i] + v2[i] for i in range(min(len(v1), len(v2)))]

def update(v: Vector, i: int, valor) -> Vector:
    u = v.copy()
    u[i] = valor
    return u
