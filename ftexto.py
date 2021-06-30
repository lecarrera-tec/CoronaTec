import math
from typing import List, Tuple

from fmate import factores


def fraccion(num: int, den: int, conSigno: bool = False,
             signoNum: bool = False, dfrac: bool = True) -> str:
    """ Texto en LaTeX de una fracción.

    Argumentos
    ----------
    num:
        Numerador
    den:
        Denominador (se asume distinto de 0)
    conSigno:
        Opcional. Imprime un signo '+' en caso de ser True. El
        predeterminado es False.
    signoNum:
        Opcional. Coloca el signo en el numerador, y no de manera
        externa.
    dfrac:
        Opcional. Utiliza dfrac de manera predeterminada para construir
        una fracción. Si False utiliza \\frac.

    Devuelve
    --------
    Simplifica y devuelve el texto en LaTeX de una fracción,
    utilizando el comando dfrac.
    """

    # Se determina el signo de la fracción.
    signo: int = 1
    assert(den != 0)
    if num < 0:
        signo *= -1
        num = abs(num)
    if den < 0:
        signo *= -1
        den = abs(den)

    # Se determina el máximo común denominador, para simplificar.
    factor: int = math.gcd(num, den)
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

    tipo = 'dfrac' if dfrac else 'frac'

    # No es una fracción.
    if den == 1:
        txt = '%s%d' % (txt, num)
    elif signoNum:
        txt = '\\%s{%s%d}{%d}' % (tipo, txt, num, den)
    else:
        txt = '%s\\%s{%d}{%d}' % (txt, tipo, num, den)

    return txt


def raiz(arg: int, indice: int = 2, conSigno: bool = False) -> str:
    """ Texto de latex para una raiz.

    Argumentos
    ----------
    arg:
        Argumento de la raíz. Debe ser positivo si `indice` es par.
    indice:
        Opcional. Índice de la raíz. 2 es el valor predeterminado.
    conSigno:
        Opcional. Imprime un signo '+' en caso de ser positivo. El
        predeterminado es False.

    Devuelve
    --------
    """

    # Se determina el signo. Negativo solo si el índice de la raíz
    # es impar.
    signo: int = 1
    assert(indice >= 2)
    assert(indice % 2 == 1 or arg >= 0)
    if (arg < 0):
        arg = -arg
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

    txt: str = ''
    if signo == -1:
        txt = '-'
    elif conSigno:
        txt = '+'

    if afuera > 1:
        txt = '%s%d' % (txt, afuera)

    if adentro > 1:
        if indice == 2:
            txt = '%s\\sqrt{%d}' % (txt, adentro)
        else:
            txt = '%s\\sqrt[%d]{%d}' % (txt, indice, adentro)

    if afuera == 1 and adentro == 1:
        txt = '%s1' % txt

    return txt


def coef(numero: int, conSigno: bool = False) -> str:
    """ Imprime el coeficiente para una variable.

    Si el número es 1 no imprime nada o sólo un +. Si el número es
    -1 imprime solo un menos. En caso contrario imprime el número (con
    signo, si así se especifica.
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
    """ Escribe la expresión como exponente si se requiere (!= 1)

    Si exp == 1 no devuelve nada. En cualquier otro caso devuelve
    "^{exp}".

    Argumentos
    ----------
    expo:
        Valor del exponente.
    Devuelve
    --------
    Un string vacío si expo == 1, "^{expo}" en cualquier otro caso.
    """

    if expo == 1:
        return ''
    else:
        return '^{%d}' % expo


def conSigno(numero: int) -> str:
    """ Imprime un número con signo.  """
    return '%+d' % numero


def decimal(numero: float, cifras: int, conSigno: bool = False) -> str:
    """ Imprime un número flotante con las cifras indicadas.

    Si el número es muy pequeño, o demasiado grande, utiliza
    notación científica para imprimirlo.

    Argumentos
    ----------
    numero:
        Número a imprimir.
    cifras:
        Cifras significativas a utilizar.
    conSigno:
        Opcional. Si el número es positivo, se agrega un + al inicio.
        El predeterminado es False.

    Devuelve
    --------
    El string del número a imprimir.
    """
    assert(cifras > 0)
    if numero == 0:
        return '0'
    signo: int = 1
    ndig: int
    if numero < 0:
        numero = -numero
        signo = -1
    if numero < pow(10, -cifras-6) or numero >= pow(10, cifras - 1):
        ftxt = '%%.%de' % (cifras - 1)
    elif numero >= 1:
        ndig = cifras - int(math.ceil(math.log10(numero)))
        ftxt = '%%.%df' % max(0, ndig)
    else:
        ndig = cifras + int(math.ceil(-math.log10(numero))) - 1
        ftxt = '%%.%df' % ndig
    return ftxt % (signo * numero)


def texto(numero: int, mil: bool = False) -> str:
    """ Convierte un número a texto.

    Argumentos
    ----------
    numero:
        Número que se quiere convertir a texto.
    mil:
        Como es una función recursiva, en caso de que siga el texto
        'mil' al final del texto que se está traduciendo.

    Devuelve
    --------
    Número como texto.
    """
    assert(numero > 0 and numero <= 999999999999)
    txt: str
    menores: List[str] = [
            'cero', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete',
            'ocho', 'nueve', 'diez', 'once', 'doce', 'trece', 'catorce',
            'quince', 'diecis\\\'eis', 'diecisiete', 'dieciocho', 'diecinueve',
            'veinte', 'veintiuno', 'veintid\\\'os', 'veintitr\\\'es',
            'veinticuatro', 'veinticinco', 'veintis\\\'eis', 'veintisiete',
            'veintiocho', 'veintinueve'
            ]
    decenas: List[str] = [
            'treinta', 'cuarenta', 'cincuenta', 'sesenta', 'setenta',
            'ochenta', 'noventa', 'cien'
            ]
    centenas: List[str] = [
            'ciento', 'doscientos', 'trescientos', 'cuatrocientos',
            'quinientos', 'seiscientos', 'setecientos', 'ochocientos',
            'novecientos', 'mil'
            ]
    miles: List[str] = [
            'cero', 'un', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete',
            'ocho', 'nueve', 'diez', 'once', 'doce', 'trece', 'catorce',
            'quince', 'diecis\\\'eis', 'diecisiete', 'dieciocho', 'diecinueve',
            'veinte', 'veintiun', 'veintid\\\'os', 'veintitr\\\'es',
            'veinticuatro', 'veinticinco', 'veintis\\\'eis', 'veintisiete',
            'veintiocho', 'veintinueve'
            ]
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
        resp = '%s %s mil' % (resp, miles[temp])
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
            resp = '%s %s' % (resp, menores[numero])
    return resp.strip()


def minCifras(numero: float, ceros: int = 3) -> str:
    """ Imprime con el mínimo número de cifras distintas de 0.

    El valor de ceros es el que decide cuando parar. Por ejemplo,
    si ceros es 2, entonces 0.20070001 se imprime como 0.2;
    si ceros es 3, entonces se imprime como 0.2007;
    y si ceros es 4 o más, imprime 0.20070001
    """
    n = 0
    temp = numero
    while isinstance(temp, float) and not round(temp, ceros).is_integer():
        temp *= 10
        n += 1
    return ('%%.%df' % n) % numero
