import math
from typing import List, Tuple

from fmate import factores
from fractions import Fraction


def fraccion(num, den: int = 1, conSigno: bool = False,
        signoNum: bool = False, dfrac: bool = True, 
        arg: str = '', coef: bool = False) -> str:
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
        una fracción. Si False utiliza \\tfrac.
    arg:
        Opcional. En caso de ser un string no vacío y el numerador sea 1 o -1.
        Si conSigno es verdadero, entonces imprime respectivamente + o -.
        Si conSigno es falso, entonces no imprime nada o - respectivamente.
    coef:
        Si es 1 o -1, se imprime sólo el signo.
        

    Devuelve
    --------
    Simplifica y devuelve el texto en LaTeX de una fracción,
    utilizando el comando dfrac.
    """

    # Se determina el signo de la fracción.
    signo: int = 1
    assert(den != 0)
    ff = Fraction(num, den)
    # Si es positivo, se imprime o no el +
    txt: str = ''
    if ff > 0:
        if conSigno:
            txt = '+'
        else:
            txt = ''
    # es negativo.
    elif ff < 0:
        txt = '-'
    else:
        return '0'

    tipo = 'dfrac' if dfrac else 'tfrac'
    num = abs(ff.numerator)
    den = ff.denominator

    # No es una fracción.
    if den == 1:
        # No es un coeficiente o es distinto de +- 1.
        if num == 1 and (coef or len(arg)):
            txt = '%s%s' % (txt, arg)
        else:
            txt = '%s%d%s' % (txt, num, arg)
    elif signoNum:
        if num == 1 and len(arg) > 0:
            txt = '\\%s{%s%s}{%d}' % (tipo, txt, arg, den)
        else:
            txt = '\\%s{%s%d%s}{%d}' % (tipo, txt, num, arg, den)
    elif num == 1 and len(arg) > 0:
        txt = '%s\\%s{%s}{%d}' % (txt, tipo, arg, den)
    else:
        txt = '%s\\%s{%d%s}{%d}' % (txt, tipo, num, arg, den)

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


def coef(numero: int, conSigno: bool = False, arg: str = '') -> str:
    """ Imprime el coeficiente para una variable.

    Si el número es 1 no imprime nada o sólo un +. Si el número es
    -1 imprime solo un menos. En caso contrario imprime el número (con
    signo, si así se especifica.
    """

    txtSigno: str
    if numero > 0 and conSigno:
        txtSigno = '+'
    elif numero > 0:
        txtSigno = ''
    elif numero < 0:
        txtSigno = '-'
        numero = abs(numero)
    else:
        assert(numero == 0)
        if len(arg) > 0:
            return ''
        else:
            return '0'
    if numero == 1:
        return '%s%s'%(txtSigno, arg)
    else:
        return '%s%d%s' % (txtSigno, numero, arg)


def expo(expo: int, arg='', coef=False) -> str:
    """ Escribe la expresión como exponente si se requiere (!= 1)

    Si expo == 0, arg no es vac\'io y coef==True, no devuelve nada.
    Si expo == 0, arg no es vac\'io y coef==False, devuelve uno.
    Si expo == 1 no devuelve nada o imprime s\'olo el argumento en
    caso de existir. En cualquier otro caso devuelve "arg^{exp}".

    Argumentos
    ----------
    expo:
        Valor del exponente.
    arg:
        Base del exponente.
    coef:
        Si el exponente es 0, no imprimir nada.
    """

    if expo == 1:
        return arg
    elif expo == 0 and len(arg) > 0:
        '' if coef else '1'
    else:
        return '%s^{%d}' % (arg,expo)


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
    if numero < pow(10, -cifras-6) or numero >= pow(10, cifras + 3):
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


def minCifras(numero: float, ceros: int = 3, maxi: int = 20) -> str:
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
    return ('%%.%df' % min(n, maxi)) % numero
