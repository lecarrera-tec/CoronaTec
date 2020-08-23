"""Leer archivos de preguntas."""

import logging
import random
from typing import List

import parser
import info

def get_latex(filename: str) -> str:
    """Función principal del módulo. Recibe como argumento la 
    dirección de un archivo, y devuelve el texto de la pregunta.

    Lo que hace es clasificar el tipo de pregunta, y llamar a la función
    correspondiente.
    """
    try:
        f = open(filename)
    except:
        logging.error('No se pudo abrir archivo "%s"' % filename) 
        return ''

    lines: List[str] = f.readlines()
    f.close()
    ignorar: bool = True
    while ignorar:
        l: str = lines.pop(0).strip()
        ignorar = len(l) == 0 or l[0] == info.COMMENT

    # Debe comenzar con el tipo de la pregunta. Leemos cuál es.
    assert(l.startswith(info.LTIPO))
    l = l.strip(info.STRIP)
    tipo: str = parser.derecha_igual(l, 'tipo')
    if tipo == 'respuesta corta':
        opcion: str = parser.derecha_igual(l, 'opcion')
        if opcion == '' or opcion == 'entero':
            return latex_corta_entera(lines)
    elif tipo == 'seleccion unica':
        orden: str = parser.derecha_igual(l, 'orden')
        return latex_unica(lines, orden)
    return ''

def latex_corta_entera(lines: List[str]) -> str:
    return ''

def latex_unica(lines: List[str], orden: str) -> str:
    logging.debug('Entrando a "latex_unica"')
    logging.debug('Orden : %s' % orden)
    logging.debug('Texto : %s', ''.join(lines))
    lista: List[str] = []
    ignorar: bool = True
    while ignorar:
        l = lines.pop(0).strip()
        ignorar = len(l) == 0 or l[0] == info.COMMENT
    if l == info.VARIABLES:
        # TODO Tenemos que ver cómo evaluar las variables.
        continuar = True
        while continuar:
            l = lines.pop(0).strip()
            continuar = l != info.PREGUNTA

    # Deberíamos estar en la pregunta. Hay que buscar si se necesitan
    # variables.
    assert(l == info.PREGUNTA)
    l = lines.pop(0)
    while not l.strip().startswith(info.LITEM):
        # TODO falta revisar si los renglones tienen parámetros.
        lista.append('    %s' % l)
        l = lines.pop(0)
    # Ahora siguen los items.
    assert(l.strip().startswith(info.LITEM))
    # TODO Hay que leer la opción de indice del item cuando corresponda.
    # Primero se va a crear una lista de los items.
    litems: List[str] = []
    item: str = ''
    l = lines.pop(0)
    while len(lines) > 0:
        if l.strip().startswith(info.LITEM):
            litems.append(item)
            item = ''
        else:
            item = '%s%s' % (item, l)
        l = lines.pop(0)
    # Falta agregar a la lista el último item
    litems.append(item)
    # Desordenamos los items.
    if orden == 'aleatorio':
        random.shuffle(litems)
    # Construimos el latex
    lista.append('    \\begin{enumerate}%s\n' % info.FORMATO_ITEM)
    for item in litems:
        lista.append('      \\item %s' % item)
    lista.append('    \\end{enumerate}\n')
    return ('%s\n' % ''.join(lista).strip())
