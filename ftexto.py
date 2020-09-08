import math
from typing import List, Tuple

import fmate

def txtFraccion(num: int, den: int, conSigno: bool = False) -> str:
    """Texto en LaTeX de una fracci\'on. 

    Argumentos
    ----------
    num:
        Numerador
    den:
        Denominador (se asume distinto de 0)
    conSigno:
        Opcional. Imprime un signo '+' en caso de ser positivo. El
        predeterminado es False.

    Devuelve
    --------
    Simplifica y devuelve el texto en LaTeX de una fracci\'on, 
    utilizando el comando dfrac.
    """

    signo: int = 1
    assert(den != 0)
    if num < 0:
        signo *= -1
        num = abs(num)
    if den < 0:
        signo *= -1
        den = abs(den)
    factor: int = math.gcd(num, den)
    num = num // factor
    den = den // factor
    texto: str
    if signo == 1:
        if conSigno:
            texto = '+'
        else:
            texto = ''
    else:
        texto = '-'

    if den == 1:
        texto = '%s%d' % (texto, num)
    else:
        texto = '%s\\dfrac{%d}{%d}' % (texto, num, den)

    return texto

def txtRaiz(arg: int, indice: int = 2, conSigno: bool = False) -> str:
    """ Texto de latex para una raiz.

    Argumentos
    ----------
    arg:
        Argumento de la ra\'iz. Debe ser positivo si `indice` es par.
    indice:
        Opcional. \'Indice de la ra\'iz. 2 es el valor predeterminado.
    conSigno:
        Opcional. Imprime un signo '+' en caso de ser positivo. El
        predeterminado es False.

    Devuelve
    --------
    """

    signo: int = 1
    assert(indice >= 2)
    assert(indice % 2 == 1 or arg >= 0)
    if (arg < 0):
        arg = abs(arg)
        signo = -1

    lfact: List[Tuple[int, int]] = fmate.factores(arg)
    afuera: int = 1
    adentro: int = 1
    for primo, numRep in lfact:
        exp_afuera, exp_adentro = divmod(numRep, indice)
        afuera *= pow(primo, exp_afuera)
        adentro *= pow(primo, exp_adentro)

    if signo == -1:
        texto = '-'
    elif conSigno:
        texto = '+'
    else:
        texto = ''
    
    if afuera > 1:
        texto = '%s%d' % (texto, afuera)

    if indice == 2:
        texto = '%s\\sqrt{%d}' % (texto, adentro)
    else:
        texto = '%s\\sqrt[%d]{%d}' % (texto, indice, adentro)

    return texto

def txtCoef(numero: int, conSigno: bool = False) -> str:
    """ Imprime el coeficiente para una variable.

    Si el n\'umero es 1 no imprime nada o s\'olo un +. Si el n\'umero es 
    -1 imprime solo un menos. En caso contrario imprime el n\'umero (con 
    signo, si as\'i se especifica.
    """

    txtSigno: str
    if numero >= 0 and conSigno:
        txtSigno = '+'
    elif numero >= 0:
        txtSigno = ''
    else:
        txtSigno = '-'
        numero = abs(numero)
    if numero == 1:
        return txtSigno
    else:
        return '%s%d' % (txtSigno, numero)

def txtExpo(expo: int) -> str:
    """ Escribe la expresi\'on como exponente si se requiere (!= 1)

    Si exp == 1 no devuelve nada. En cualquier otro caso devuelve 
    "^{exp}".

    Argumentos
    ----------
    expo:
        Valor del exponente.
    Devuelve
    --------
    Un string vac\'io si expo == 1, "^{expo}" en cualquier otro caso.
    """

    if expo == 1:
        return ''
    else:
        return '^{%d}' % expo
