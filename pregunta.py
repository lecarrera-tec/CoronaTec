"""Leer archivos de preguntas."""

import logging
import random
from typing import List
import sys

import parser
import Info
import TPreg
from respuesta import Respuesta

def get_latex(filename: str) -> str:
    """Recibe como argumento la dirección de un archivo, y devuelve el 
    texto de la pregunta.

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
    texto: str
    while ignorar:
        l: str = lines.pop(0).strip()
        ignorar = len(l) == 0 or l[0] == Info.COMMENT

    # Debe comenzar con el tipo de la pregunta. Leemos cuál es.
    assert(l.startswith(Info.LTIPO))
    l = l.strip(Info.STRIP)
    tipo: str = parser.derecha_igual(l, 'tipo')
    if tipo == 'respuesta corta':
        opcion: str = parser.derecha_igual(l, 'opcion')
        if opcion == '' or opcion == 'entero':
            texto = latex_corta_entera(lines)
    elif tipo == 'seleccion unica':
        orden: str = parser.derecha_igual(l, 'orden')
        texto = latex_unica(lines, orden)

    # Queda aún algo muy importante por hacer, y es modificar el path de 
    # las figuras que se incluyan: \includegraphics[opciones]{path}
    # Primero comenzamos extrayendo el path hasta el folder donde está
    # el archivo.
    idx: int = filename.rfind('/')
    path: str = filename[:idx]
    # Ahora buscamos cada includegraphics, y le agregamos el path.
    idx = 0
    while True:
        idx = texto.find('\\includegraphics', idx)
        if idx == -1:
            break
        idx = texto.find('{', idx)
        assert(idx != -1)
        texto = '%s{%s/%s' % (texto[:idx], path, texto[idx+1:])

    return texto

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
        ignorar = len(l) == 0 or l[0] == Info.COMMENT
    if l == Info.VARIABLES:
        # TODO Tenemos que ver cómo evaluar las variables.
        continuar = True
        while continuar:
            l = lines.pop(0).strip()
            continuar = l != Info.PREGUNTA

    # Deberíamos estar en la pregunta. Hay que buscar si se necesitan
    # variables.
    assert(l == Info.PREGUNTA)
    l = lines.pop(0)
    texto: List[str] = []
    while not l.strip().startswith(Info.LITEM):
        # TODO falta revisar si los renglones tienen parámetros.
        texto.append('    %s\n' % l)
        l = lines.pop(0)
    lista.append('%s\n%s' % (''.join(texto).rstrip(), '    \\nopagebreak\n'))
    # Ahora siguen los items.
    texto = []
    assert(l.strip().startswith(Info.LITEM))
    # TODO Hay que parsear cada item por si está parametrizado.
    # TODO Hay que leer la opción de indice del item cuando corresponda.
    # Primero se va a crear una lista de los items.
    litems: List[str] = []
    item: str = ''
    l = lines.pop(0)
    while len(lines) > 0:
        if l.strip().startswith(Info.LITEM):
            litems.append('%s\n      \\nopagebreak\n' % ''.join(texto).rstrip())
            texto = []
        else:
            texto.append('%s' % l)
        l = lines.pop(0)
    # Falta agregar a la lista el último item
    litems.append('%s\n      \\nopagebreak\n' % ''.join(texto).rstrip())
    # Desordenamos los items.
    if orden == 'aleatorio':
        random.shuffle(litems)
    # Construimos el latex
    lista.append('    \\begin{enumerate}%s\n' % Info.FORMATO_ITEM)
    for item in litems:
        lista.append('      \\item %s' % item)
    lista.append('    \\end{enumerate}\n')
    return ('%s\n' % ''.join(lista).strip())

def get_respuesta(filename: str) -> Respuesta:
    """Recibe como argumento la dirección de un archivo, y devuelve una
    instancia de un objeto Respuesta.

    Lo que hace es clasificar el tipo de pregunta, y llamar a la función
    correspondiente.
    """
    try:
        f = open(filename)
    except:
        logging.error('No se pudo abrir archivo "%s"' % filename) 
        sys.exit()

    lines: List[str] = f.readlines()
    f.close()
    ignorar: bool = True
    while ignorar:
        l: str = lines.pop(0).strip()
        ignorar = len(l) == 0 or l[0] == Info.COMMENT

    # Debe comenzar con el tipo de la pregunta. Leemos cuál es.
    assert(l.startswith(Info.LTIPO))
    l = l.strip(Info.STRIP)
    tipo: str = parser.derecha_igual(l, 'tipo')
    if tipo == 'respuesta corta':
        opcion: str = parser.derecha_igual(l, 'opcion')
        if opcion == '' or opcion == 'entero':
            return respuesta_corta_entera(lines)
    elif tipo == 'seleccion unica':
        orden: str = parser.derecha_igual(l, 'orden')
        return respuesta_unica(lines, orden)

    logging.critical('Tipo de pregunta desconocido: %s' % l)
    sys.exit()

def respuesta_corta_entera(lines: List[str]):
    assert(False)
    return Respuesta(TPreg.NINGUNA)

def respuesta_unica(lines: List[str], orden: str):
    logging.debug('Entrando a "respuesta_unica"')
    logging.debug('Orden : %s' % orden)
    logging.debug('Texto : %s', ''.join(lines))
    ignorar: bool = True
    resp = Respuesta(TPreg.UNICA)
    while ignorar:
        l = lines.pop(0).strip()
        ignorar = len(l) == 0 or l[0] == Info.COMMENT
    if l == Info.VARIABLES:
        # TODO Tenemos que ver cómo evaluar las variables.
        continuar = True
        while continuar:
            l = lines.pop(0).strip()
            continuar = l != Info.PREGUNTA

    # Deberíamos estar en la pregunta. Nos la brincamos, porque no se
    # debería de llamar a ninguna función random aquí.
    assert(l == Info.PREGUNTA)
    l = lines.pop(0)
    while not l.strip().startswith(Info.LITEM):
        l = lines.pop(0)
    # Ahora siguen los items.
    assert(l.strip().startswith(Info.LITEM))
    # TODO Hay que parsear cada item por si está parametrizado.
    # TODO Hay que leer la opción de indice del item cuando corresponda.
    # Se incluyen las opciones.
    litems : List[int] = [0]
    l = lines.pop(0)
    while len(lines) > 0:
        if l.strip().startswith(Info.LITEM):
            litems.append(litems[-1] + 1)
        l = lines.pop(0)
    # Desordenamos los items.
    if orden == 'aleatorio':
        resp.add_opcion(TPreg.ALEATORIO)
        random.shuffle(litems)
    resp.add_respuesta(litems.index(0))
    return resp
