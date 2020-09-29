"""Funciones que ayudan a leer opciones y parámetros."""
import logging
from typing import Any, List, Dict
import sys

from diccionarios import DGlobal
import ftexto as txt


def derechaIgual(expresion: str, izq: str) -> str:
    """Extrae el expresión a la derecha de un igual.

    Argumentos
    ----------
    expresion:
        Texto que puede estar formado por varios iguales separados por
        comas. Se busca el igual con el respectivo lado izquierdo.
    izq:
        Expresión a buscar al lado izquierda del igual.

    Devuelve
    --------
    El texto que esté al lado derecho del igual de la expresión
    referida por ``izq``. Si la expresión no se encuentra, devuelve
    un string vacío.
    """

    # Separamos el expresion en cada una de las opciones.
    lista: List[str] = expresion.split(',')

    for elem in lista:
        # Buscamos el igual para separar el string.
        idx: int = elem.find('=')
        # No tiene igual; seguimos con el siguiente elemento.
        if idx == -1:
            continue
        # Extraemos el lado izquierdo.
        temp: str = elem[0:idx].strip()
        # Si el lado izquierdo no coincide, continuamos
        if temp != izq:
            continue
        # El lado izquierdo coincide. Devolvemos lo que hay al lado
        # derecho del igual.
        temp = elem[idx+1:].strip()
        return temp
    # No se encontró nada.
    return ''


def evaluarParam(linea: str, dLocal: Dict[str, Any],
                 dparams: Dict[str, Any]) -> None:
    """Función que evalúa las variables dadas por el usuario.

    Observe que la función no devuelve nada. Simplemente actualiza los
    diccionarios dados como argumentos.
    Argumentos
    ----------
    linea:
        Línea de texto. Se espera que sea de la forma:
        <nombre_variable>[, <nombre_variable]* = <expresion evaluable>
    dLocal:
        Diccionario que incluye todas las funciones y los parámetros ya
        definidos por el usuario. Se actualiza con la variable que se
        lea en esta línea.
    dparams:
        Diccionario de las variables del usuario. Se actualiza también
        con la variable dada por el usuario en esta línea. La
        redundancia se debe a que el diccionario local se va a
        restringir para el caso del texto de la pregunta.
    """

    # Se separa solamente el primer igual que se encuentre. Podría haber
    # iguales en la expresión a evaluar y hay que dejarlos intactos.
    logging.debug('def. de variable: `%s`' % linea)
    lista: List[str] = linea.split('=', 1)
    variables: List[str] = lista[0].strip().split(',')
    # Revisar que el nombre de la variable no corresponda a ninguna
    # función.
    for var in variables:
        var = var.strip()
    logging.debug('Evaluar: `%s`' % lista[1].strip())
    resultado: Any = eval(lista[1].strip(), DGlobal, dLocal)
    logging.debug('Evaluado: `%s`' % str(resultado))
    n: int = len(variables)
    logging.debug('Numero de variables: %d' % n)
    if n == 1:
        variables[0] = variables[0].strip()
        logging.debug('  %s: %s' % (variables[0], str(resultado)))
        dparams[variables[0]] = resultado
        dLocal[variables[0]] = resultado
    elif n == len(resultado):
        for i in range(n):
            variables[i] = variables[i].strip()
            logging.debug('  %s: %s' % (variables[i], str(resultado[i])))
            dparams[variables[i]] = resultado[i]
            dLocal[variables[i]] = resultado[i]
    else:
        logging.critical('El numero de iterables no coincide:')
        logging.critical('%s = %s' % (','.join(variables), str(resultado)))
        sys.exit()


def update(linea: str, dLocal: Dict[str, Any], cifras: int = 3) -> str:
    """Actualiza cualquier @-expresión que haya que evaluar en el texto.

    Las @-expresiones pueden ser de 3 tipos:
    * Texto (string): simplemente se imprime igual.
    * Entero (int): se imprime el texto del entero.
    * Flotante (float): Aquí es donde hay que tomar decisiones. El
    número de cifras significativas se da por la variable ``cifras``.
    Argumentos
    ----------
    linea:
        Línea de texto. La @-expresión debe estar completamente
        contenida en una sola línea de texto.
    dLocal:
        Diccionario con las variables definidas por el usuario y
        funciones accesibles. No se actualiza ni se agregan valores
        nuevos.
    cifras:
        Número de cifras significativas a utilizar con los números
        de tipo flotante.
    Devuelve
    --------
    El texto de la pregunta con las @-expresiones sustituidas por su
    respectivo valor.
    """

    separar: List[str] = linea.split('@')
    if len(separar) == 1:
        return linea
    unir: List[str] = [separar.pop(0)]
    ind_fin: int
    txt_expr: str
    evaluada: Any
    txt_evaluacion: str
    for txt_expr in separar:
        ind_fin = __fin_expr_arroba__(txt_expr)
        logging.debug('Expresion a evaluar: `%s`' % txt_expr[1:ind_fin])
        evaluada = eval(txt_expr[1:ind_fin], DGlobal, dLocal)
        txt_evaluacion = __convertir_a_texto__(evaluada, cifras)
        txt_expr = txt_expr[ind_fin+1:]
        unir.append('%s%s' % (txt_evaluacion, txt_expr))
    return ''.join(unir)


def __fin_expr_arroba__(txt_expr: str) -> int:
    key: str
    key = txt_expr[0]
    if key == '(':
        ind_fin = txt_expr.find(')', 1)
    elif key == '[':
        ind_fin = txt_expr.find(']', 1)
    elif key == '{':
        ind_fin = txt_expr.find('}', 1)
    elif key == '<':
        ind_fin = txt_expr.find('>', 1)
    else:
        ind_fin = txt_expr.find(key, 1)
    if ind_fin == -1:
        logging.critical('No se encontr\'o cierre de @-expresi\'on:')
        logging.critical('   %s', txt_expr)
        sys.exit()
    return ind_fin


def __convertir_a_texto__(expr: Any, cifras: int) -> str:
    """ Se convierte a texto la expresi\'on."""
    resp: str
    if isinstance(expr, float):
        resp = txt.decimal(expr, cifras)
    elif isinstance(expr, set):
        resp = '\\{%s\\}' % str(expr)[1:-1].replace('\'', '')
    else:
        resp = str(expr)
    return resp
