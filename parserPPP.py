"""Funciones que ayudan a leer opciones y parámetros."""
import logging
from math import log10
from typing import Any, List, Dict

from diccionarios import DGlobal, DFunciones, DFunRandom
from fmate import digSignif
from ftexto import txtFloat

def derechaIgual(expresion : str, izq : str) -> str:
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

def evaluarParam(linea: str, dLocal: Dict[str, Any], dparams: Dict[str, Any]) -> None:
    """Función que evalúa las variables dadas por el usuario.

    Observe que la función no devuelve nada. Simplemente actualiza los
    diccionarios dados como argumentos.
    Argumentos
    ----------
    linea:
        Línea de texto. Se espera que sea de la forma:
        ``<nombre_de_variable> = <expresion evaluable>``
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
    nombreVariable: str = lista[0].strip()
    # Revisar que el nombre de la variable no corresponda a ninguna
    # función.
    if (nombreVariable in DFunRandom) or (nombreVariable in DFunciones):
        logging.error('Nombre de variable es una palabra reservada.')
        return
    logging.debug('Evaluar: `%s`' % lista[1].strip())
    resultado: Any = eval(lista[1].strip(), DGlobal, dLocal)
    logging.debug('Evaluado: `%s`' % str(resultado))
    dparams[nombreVariable] = resultado
    dLocal[nombreVariable] = resultado

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
    key: str
    fin: int
    texpr: str
    expr: Any
    for texpr in separar:
        key = texpr[0]
        if key == '(':
            fin = texpr.find(')', 1)
        elif key == '[':
            fin = texpr.find(']', 1)
        elif key == '{':
            fin = texpr.find('}', 1)
        elif key == '<':
            fin = texpr.find('>', 1)
        else:
            fin = texpr.find(key, 1)
        assert(fin > 0)
        logging.debug('Expresion a evaluar: `%s`' % texpr[1:fin])
        expr = eval(texpr[1:fin], DGlobal, dLocal)
        if isinstance(expr, str):
            unir.append('%s%s' % (expr, texpr[fin+1:]))
        elif isinstance(expr, int):
            unir.append('%d%s' % (expr, texpr[fin+1:]))
        elif isinstance(expr, float):
            unir.append('%s%s' % (txtFloat(expr, cifras), texpr[fin+1:]))
        # No tenemos idea de qué tipo es.
        else:
            unir.append('%s%s' % (str(expr), texpr[fin+1:]))
    return ''.join(unir)
