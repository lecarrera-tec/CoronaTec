import math
from typing import List, Tuple

def factores(numero: int) -> List[Tuple[int, int]]:
    """ Lista de factores de un entero positivo.

    Devuelve una lista de Tuplas, donde el primer valor es el factor
    primo, y el segundo el n\'umero de veces que se repite.

    Argumentos
    ----------
    numero:
        Entero positivo a factorizar.

    Devulve
    -------
        Lista de tuplas, donde el primer elemento de cada tupla es el
        n\'umero primo que es factor, y el segundo el n\'umero de veces
        que est\'a presente.
    """

    assert(numero >= 0)
    factores: List[Tuple[int, int]] = []
    counter: int = 0
    while (numero % 2 == 0):
        numero = numero // 2
        counter += 1
    if counter > 0:
        factores.append((2, counter))

    i = 3
    while i * i < numero:
        counter = 0
        while (numero % i == 0):
            numero = numero // i
            counter += 1
        if counter > 0:
            factores.append((i, counter))
        i += 2
    factores.append((numero, 1))
    return factores

def digSignif(numero: float, digitos: int):
    signo: int = 1
    if numero == 0:
        return numero
    if numero < 0:
        signo = -1
        numero = -numero
    exp: int = math.ceil(math.log10(numero)) - 1
    pot10: int = pow(10, exp)
    numero /= pot10
    assert(1 <= numero and numero < 10)
    numero = round(numero, digitos - 1)
    return signo * numero * pot10

def descomponer(numero: float) -> Tuple[float, int]:
    if numero == 0:
        return (0, 0)
    signo: int = 1
    if numero < 0:
        signo = -1
        numero = -numero
    exp: int = math.ceil(math.log10(numero)) - 1
    numero /= pow(10, exp)
    return (signo * numero, exp)
