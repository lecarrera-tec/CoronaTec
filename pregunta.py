"""Leer archivos de preguntas."""

import logging
import random
from typing import Any, List, Dict
import sys

import parserPPP
import Info
import TPreg
from respuesta import Respuesta
from diccionarios import DFunRandom, DFunciones

def get_latex(filename: str, dParams: Dict[str, Any]) -> str:
    """Genera el código LaTeX de la pregunta.

    Lo que hace es clasificar el tipo de pregunta, y llamar a la 
    función correspondiente.

    Argumentos
    ----------
    filename:
        Path del archivo de la pregunta.
    dParams:
        Diccionario de parámetros definidos por el usuario.

    Devuelve
    --------
    El texto LaTeX de la pregunta.
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
    tipo: str = parserPPP.derechaIgual(l, 'tipo')
    if tipo == 'respuesta corta':
        opcion: str = parserPPP.derechaIgual(l, 'opcion')
        if opcion == '' or opcion == 'entero':
            texto = latex_corta_entera(l, lines, dParams)
    elif tipo == 'seleccion unica':
        texto = latex_unica(l, lines, dParams)

    # Queda aún algo muy importante por hacer, y es modificar el path 
    # de las figuras que se incluyan: \includegraphics[opciones]{path}
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

def latex_corta_entera(l: str, lines: List[str], dParams: Dict[str, Any]) -> str:
    return ''

def latex_unica(l: str, lines: List[str], dParams: Dict[str, Any]) -> str:
    """LaTeX de pregunta de selección única.

    Argumentos
    ---------
    l:
        Primera línea. Para leer las opciones específicas.
    linea:
        Resto de las líneas de texto.
    dParams:
        Diccionario de variables definidas por el usuario.

    Devuelve
    --------
    Texto LaTeX de la pregunta, con los parámetros ya sustituidos.
    """

    # TODO Faltan leer los parámetros de la pregunta que se encuentran
    # en ``l``
    orden = 'aleatorio'
    logging.debug('Entrando a "latex_unica"')
    logging.debug('Texto : %s', ''.join(lines))
    lista: List[str] = []
    ignorar: bool = True
    while ignorar:
        l = lines.pop(0).strip()
        ignorar = len(l) == 0 or l[0] == Info.COMMENT
    # Definiendo diccionario.
    dLocal: Dict[str, Any] = {**dParams, **DFunRandom, **DFunciones}
    if l == Info.VARIABLES:
        while True:
            l = lines.pop(0).strip()
            if l == Info.PREGUNTA:
                break
            elif len(l) == 0 or l[0] == Info.COMMENT:
                continue
            parserPPP.evaluarParam(l, dLocal, dParams)

    # Deberíamos estar en la pregunta. Hay que buscar si se necesitan
    # variables.
    assert(l == Info.PREGUNTA)
    # Redefinimos el diccionario, eliminando las preguntas que generan
    # números aleatorios.
    dLocal = {**dParams, **DFunciones}
    l = lines.pop(0)
    texto: List[str] = []
    while not l.strip().startswith(Info.LITEM):
        # Agregamos la l\'inea de texto actualizando las @-expresiones.
        texto.append('    %s' % parserPPP.update(l, dLocal))
        l = lines.pop(0)
    lista.append('%s\n%s' % (''.join(texto).rstrip(), '    \\nopagebreak\n'))
    # Ahora siguen los items.
    texto = []
    assert(l.strip().startswith(Info.LITEM))
    # TODO Hay que parsear cada item por si está parametrizado.
    # TODO Hay que leer la opción de indice del item cuando 
    # corresponda. Primero se va a crear una lista de los items.
    litems: List[str] = []
    item: str = ''
    while len(lines) > 0:
        l = lines.pop(0)
        # Un nuevo item. Finalizamos el anterior.
        if l.strip().startswith(Info.LITEM):
            # TODO falta revisar opciones como \'indice.
            litems.append('%s\n\n' % ''.join(texto).rstrip())
            texto = []
        else:
            texto.append('%s' % parserPPP.update(l, dLocal))
    # Falta agregar a la lista el último item
    litems.append('%s\n\n' % ''.join(texto).rstrip())
    # Desordenamos los items.
    if orden == 'aleatorio':
        random.shuffle(litems)
    # Construimos el latex
    lista.append('    \\begin{enumerate}%s\n' % Info.FORMATO_ITEM)
    for item in litems:
        lista.append('      \\item %s' % item)
    lista.append('    \\end{enumerate}\n')
    return ('%s\n' % ''.join(lista).strip())

def get_respuesta(filename: str, dParams: Dict[str, Any]) -> Respuesta:
    """
    Recibe como argumento la dirección de un archivo, y devuelve una
    instancia de un objeto Respuesta.

    Lo que hace es clasificar el tipo de pregunta, y llamar a la 
    función correspondiente.
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
    tipo: str = parserPPP.derechaIgual(l, 'tipo')
    if tipo == 'respuesta corta':
        opcion: str = parserPPP.derechaIgual(l, 'opcion')
        if opcion == '' or opcion == 'entero':
            return respuesta_corta_entera(lines)
    elif tipo == 'seleccion unica':
        orden: str = parserPPP.derechaIgual(l, 'orden')
        return respuesta_unica(l, lines, dParams)

    logging.critical('Tipo de pregunta desconocido: %s' % l)
    sys.exit()

def respuesta_corta_entera(lines: List[str]):
    assert(False)
    return Respuesta(TPreg.NINGUNA)

def respuesta_unica(
            l: str, lines: List[str], dParams: Dict[str, Any]) -> Respuesta:
    """Objeto Respuesta de pregunta de selección única.

    Argumentos
    ---------
    l:
        Primera línea. Para leer las opciones específicas.
    linea:
        Resto de las líneas de texto.
    dParams:
        Diccionario de variables definidas por el usuario.

    Devuelve
    --------
    Objeto de tipo Respuesta de la pregunta, con los parámetros ya 
    sustituidos.
    """

    logging.debug('Entrando a "respuesta_unica"')
    logging.debug('Texto : %s', ''.join(lines))
    # TODO Se tienen que extraer las opciones de la pregunta.
    orden = parserPPP.derechaIgual(l, 'orden')

    ignorar: bool = True
    resp = Respuesta(TPreg.UNICA)
    while ignorar:
        l = lines.pop(0).strip()
        ignorar = len(l) == 0 or l[0] == Info.COMMENT
    dLocal: Dict[str, Any] = {**dParams, **DFunRandom, **DFunciones}
    if l == Info.VARIABLES:
        while True:
            l = lines.pop(0).strip()
            if l == Info.PREGUNTA:
                break
            elif len(l) == 0 or l[0] == Info.COMMENT:
                continue
            else:
                parserPPP.evaluarParam(l, dLocal, dParams)

    # Deberíamos estar en la pregunta. Nos la brincamos, porque no se
    # debería de llamar a ninguna función random aquí.
    assert(l == Info.PREGUNTA)
    l = lines.pop(0)
    while not l.strip().startswith(Info.LITEM):
        l = lines.pop(0)
    # Ahora siguen los items.
    assert(l.strip().startswith(Info.LITEM))
    # TODO Hay que leer la opción de indice del item cuando 
    # corresponda. Se incluyen las opciones.
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
