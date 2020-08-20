"""Leer archivos de preguntas."""

import parser
import info
from typing import List

def get_latex(filename : str) -> List[str]:
    """Función principal.

    Lo que hace es clasificar el tipo de pregunta, y llamar a la función
    correspondiente.
    """
    f = open(filename)
    lines: List[str] = f.readlines()
    f.close()
    ignorar : bool = True
    while ignorar:
        l : str = lines.pop(0).strip()
        ignorar = len(l) == 0 or l[0] == info.COMMENT

    # Debe comenzar con el tipo de la pregunta. Leemos cuál es.
    assert(l == info.LTIPO)
    tipo : str = parser.derecha_igual(l, info.LTIPO)
    if tipo == 'respuesta corta':
        opcion : str = parser.derecha_igual(l, 'opcion')
        if opcion == '' or opcion == 'entero':
            return latex_corta_entera(lines)
    elif tipo == 'seleccion unica':
        orden : str = parser.derecha_igual(l, 'orden')
        return latex_unica(lines, orden)

    return []

def latex_corta_entera(lines : List[str]) -> List[str]:
    return []

def latex_unica(lines : List[str], orden : str):
    ignorar : bool = True
    while ignorar:
        l = lines.pop(0).strip()
        ignorar = len(l) == 0 or l[0] = info.comment
    if l == info.VARIABLES:
        # TODO Tenemos que ver c\'omo evaluar las variables.
    # Deber\'iamos estar en la pregunta. Hay que buscar si se necesitan
    # variables.
    assert(l == info.PREGUNTA)
    l = lines.pop(0)
    while (l.strip() != info.ITEM):

    return []
