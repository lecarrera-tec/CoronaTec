from math import gcd, log10
from typing import List, Tuple

from fmate import factores

def fraccion(num: int, den: int, conSigno: bool = False) -> str:
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

    # Se determina el signo de la fracci\'on.
    signo: int = 1
    assert(den != 0)
    if num < 0:
        signo *= -1
        num = abs(num)
    if den < 0:
        signo *= -1
        den = abs(den)

    # Se determina el m\'aximo com\'un denominador, para simplificar.
    factor: int = gcd(num, den)
    num = num // factor
    den = den // factor

    # Si es positivo, se imprime o no el +
    txt: str
    if signo == 1:
        if conSigno:
            txt = '+'
        else:
            txt = ''
    # es negativo.
    else:
        txt = '-'

    # No es una fracci\'on.
    if den == 1:
        txt = '%s%d' % (txt, num)
    else:
        txt = '%s\\dfrac{%d}{%d}' % (txt, num, den)

    return txt

def raiz(arg: int, indice: int = 2, conSigno: bool = False) -> str:
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

    # Se determina el signo. Negativo solo si el \'indice de la ra\'iz
    # es impar.
    signo: int = 1
    assert(indice >= 2)
    assert(indice % 2 == 1 or arg >= 0)
    if (arg < 0):
        arg = abs(arg)
        signo = -1

    # Se obtienen los factores, y se determina lo que queda afuera
    # y lo que queda adentro.
    lfact: List[Tuple[int, int]] = factores(arg)
    afuera: int = 1
    adentro: int = 1
    for primo, numRep in lfact:
        exp_afuera, exp_adentro = divmod(numRep, indice)
        afuera *= pow(primo, exp_afuera)
        adentro *= pow(primo, exp_adentro)

    if signo == -1:
        txt = '-'
    elif conSigno:
        txt = '+'
    else:
        txt = ''

    if afuera > 1:
        txt = '%s%d' % (txt, afuera)

    if adentro > 1:
        if indice == 2:
            txt = '%s\\sqrt{%d}' % (txt, adentro)
        else:
            txt = '%s\\sqrt[%d]{%d}' % (txt, indice, adentro)

    return txt

def coef(numero: int, conSigno: bool = False) -> str:
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

def expo(expo: int) -> str:
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

def conSigno(numero: int) -> str:
    return '%+d' % numero

def decimal(numero: float, cifras: int) -> str:
    if numero < pow(10, -2*cifras-1) or numero >= pow(10, cifras - 1):
        ftxt = '%%.%de' % (cifras - 1)
    elif numero >= 1:
        ftxt = '%%.%df' % (cifras - int(log10(numero)) - 1)
    else:
        ftxt = '%%.%df' % (cifras + int(-log10(numero)))
    return ftxt % numero

def texto(numero: int, mil: bool = False) -> str:
    assert(numero > 0 and numero <= 999999999999)
    txt: str
    teens: List[str] = ['cero', 'uno', 'dos', 'tres', 'cuatro', 'cinco',
            'seis', 'siete', 'ocho', 'nueve', 'diez', 'once', 'doce', 'trece',
            'catorce', 'quince', 'diecis\\\'eis', 'diecisiete', 'dieciocho',
            'diecinueve', 'veinte', 'veintiuno', 'veintid\\\'os',
            'veintitr\\\'es', 'veinticuatro', 'veinticinco', 'veintis\\\'eis',
            'veintisiete', 'veintiocho', 'veintinueve']
    decenas: List[str] = ['treinta', 'cuarenta', 'cincuenta', 'sesenta',
            'setenta', 'ochenta', 'noventa', 'cien']
    centenas: List[str] = ['ciento', 'doscientos', 'trescientos',
            'cuatrocientos', 'quinientos', 'seiscientos', 'setecientos',
            'ochocientos', 'novecientos', 'mil']
    miles: List[str] = ['cero', 'un', 'dos', 'tres', 'cuatro', 'cinco',
            'seis', 'siete', 'ocho', 'nueve', 'diez', 'once', 'doce', 'trece',
            'catorce', 'quince', 'diecis\\\'eis', 'diecisiete', 'dieciocho',
            'diecinueve', 'veinte', 'veintiun', 'veintid\\\'os',
            'veintitr\\\'es', 'veinticuatro', 'veinticinco', 'veintis\\\'eis',
            'veintisiete', 'veintiocho', 'veintinueve']
    resp = ''
    if numero >= 2000000:
        temp = numero // 1000000
        numero = numero % 1000000
        resp = '%s millones' % texto(temp, mil)
    if numero >= 30000:
        temp = numero // 1000
        numero = numero % 1000
        resp = '%s %s mil' % (resp, texto(temp, True))
    if numero >= 2000:
        temp = numero // 1000
        numero = numero % 1000
        if mil:
            resp = '%s %s mil' % (resp, miles[temp])
        else:
            resp = '%s %s mil' % (resp, teens[temp])
    if numero >= 1000:
        numero = numero % 1000
        resp = 'mil'
    if numero > 100:
        temp = numero // 100 - 1
        numero = numero % 100
        resp = '%s %s' % (resp, centenas[temp])
    if numero >= 30:
        temp = numero // 10 - 3
        numero = numero % 10
        if numero > 0:
            resp = '%s %s y' % (resp, decenas[temp])
        else:
            resp = '%s %s' % (resp, decenas[temp])
    if numero > 0:
        if mil:
            resp = '%s %s' % (resp, miles[numero])
        else:
            resp = '%s %s' % (resp, teens[numero])
    return resp.strip()
