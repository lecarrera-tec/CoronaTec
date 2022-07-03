"""Archivos de preguntas."""

import logging
from math import inf
import os
import random
import sys
from typing import Any, List, Dict, Tuple, Union
from fractions import Fraction

import parserPPP
import Info
import TPreg
from respuesta import Respuesta
from diccionarios import DFunRandom, DFunciones, DGlobal

Numero = Union[int, float]
Item = Tuple[bool, str]


class Pregunta:
    """Información básica de una pregunta.

    Atributos
    ---------
    puntaje: float
        Puntos asignados a la pregunta.
    origen: str
        Origen de la pregunta (o carpeta al banco de preguntas)
    muestra: int
        En caso de un banco de preguntas, tamaño de la muestra.
    columnas: int
        Número de columnas que se imprimen las opciones en
        caso de que sea de selección única. 1 es por defecto.
    bloque: int
        0 si no se está en un bloque.
        1 si es el inicio de un bloque.
        2 si se está en el medio de un bloque.
        -1 si se está en la última pregunta de un bloque.
    """
    def __init__(self, puntaje: float, origen: str, muestra: int,
            bloque: bool, columnas: int):
        self.puntaje: float = puntaje
        self.origen: str = origen
        self.muestra: int = muestra
        self.bloque: int = 2 * int(bloque)
        self.columnas: int = columnas

    def es_bloque(self) -> bool:
        return self.bloque != 0

    def set_ultima(self):
        self.bloque = -1

    def es_ultima(self) -> bool:
        return self.bloque == -1

    def es_primera(self) -> bool:
        return self.bloque == 1

    def set_primera(self):
        self.bloque = 1

    def get_puntaje(self) -> float:
        return self.puntaje

    def get_muestra(self) -> int:
        return self.muestra

    def get_columnas(self) -> int:
        return self.columnas

    def get_latex(self, filename: str, dParams: Dict[str, Any],
                  revisar: bool = False) -> str:
        """Genera el código LaTeX de la pregunta.

        Lo que hace es clasificar el tipo de pregunta, y llamar a la
        función correspondiente.

        Argumentos
        ----------
        filename:
            Path del archivo de la pregunta.
        dParams:
            Diccionario de parámetros definidos por el usuario.
        revisar:
            Para especificar que se está en la opción de visualizar,
            y que se debe especificar/imprimir la respuesta.

        Devuelve
        --------
        El texto LaTeX de la pregunta.
        """
        # Se obtienen todas las lineas del archivo y se cierra.
        try:
            f = open(filename)
        except FileNotFoundError:
            logging.error('No se pudo abrir archivo "%s"' % filename)
            return ''
        lsTexto: List[str] = f.readlines()
        f.close()

        texto: str
        linea: str
        # Se ignoran los comentarios.
        ignorar: bool = True
        while ignorar:
            linea = lsTexto.pop(0).strip()
            ignorar = len(linea) == 0 or linea.startswith(Info.COMMENT)

        # Debe comenzar con el tipo de la pregunta. Leemos cuál es.
        assert(linea.startswith(Info.LTIPO))
        linea = linea.strip(Info.STRIP)
        tipo: str = parserPPP.derechaIgual(linea, 'tipo')
        if tipo == 'respuesta corta':
            if self.puntaje == 0:
                logging.critical('Pregunta de respuesta corta vale 0 puntos.')
                assert(self.puntaje > 0)
            texto = latex_corta(linea, lsTexto, dParams, revisar)
        elif tipo == 'seleccion unica':
            if self.puntaje == 0:
                logging.critical('Pregunta de seleccion unica vale 0 puntos.')
                assert(self.puntaje > 0)
            texto = latex_unica(linea, lsTexto, dParams, revisar, self.get_columnas())
        elif tipo == 'encabezado':
            if self.puntaje > 0:
                logging.critical('Se le asignaron puntos al encabezado.')
                assert(self.puntaje == 0)
            texto = latex_encabezado(linea, lsTexto, dParams)
        else:
            logging.critical('Tipo de pregunta desconocido: `%s`' % linea)
            sys.exit()

        # Modificar path de figuras
        texto = __path_graphics__(filename, texto)
        return texto


def get_respuesta(filename: str, dParams: Dict[str, Any]) -> Respuesta:
    """ Constructor de la respuesta.

    Lo que hace es clasificar el tipo de pregunta, y llamar a la
    función correspondiente.

    Argumentos
    ----------
    filename:
        Nombre del archivo donde se encuentra la pregunta.
    dParams:
        Diccionario de los parámetros definidos por el usuario.

    Devuelve
    --------
        Objeto de tipo Respuesta de la pregunta, con los parámetros
        ya sustituidos.
    """

    # Se abre el archivo, se leen y guardan las líneas y se cierra
    # el archivo.
    try:
        f = open(filename)
    except FileNotFoundError:
        logging.error('No se pudo abrir archivo "%s"' % filename)
        sys.exit()
    lsTexto: List[str] = f.readlines()
    f.close()

    # Ignorando comentarios y líneas en blanco.
    ignorar: bool = True
    while ignorar:
        linea: str = lsTexto.pop(0).strip()
        ignorar = len(linea) == 0 or linea.startswith(Info.COMMENT)

    # Debe comenzar con el tipo de la pregunta. Leemos cuál es.
    assert(linea.startswith(Info.LTIPO))
    linea = linea.strip(Info.STRIP)
    tipo: str = parserPPP.derechaIgual(linea, 'tipo')
    if tipo == 'respuesta corta':
        return respuesta_corta(linea, lsTexto, dParams)
    elif tipo == 'seleccion unica':
        return respuesta_unica(linea, lsTexto, dParams)
    elif tipo == 'encabezado':
        return respuesta_encabezado(linea, lsTexto, dParams)

    logging.error('Tipo de pregunta desconocido: %s' % linea)
    return Respuesta(TPreg.NINGUNA)


def latex_unica(opciones: str, lsTexto: List[str],
        dParams: Dict[str, Any], revisar: bool, columnas: int) -> str:
    """LaTeX de pregunta de selección única.

    Argumentos
    ---------
    opciones:
        Primera línea. Para leer las opciones específicas.
    linea:
        Resto de las líneas de texto.
    dParams:
        Diccionario de variables definidas por el usuario.
    revisar:
        Para especificar que se está en la opción de visualizar, y que
        se debe especificar/imprimir la respuesta.
    columnas: # de columnas que se utilizar para imprimir las opciones.

    Devuelve
    --------
        Texto LaTeX de la pregunta, con los parámetros ya sustituidos.
    """

    logging.debug('Entrando a "latex_unica"')
    logging.debug('Texto: %s', ''.join(lsTexto))

    # TODO Faltan leer los parámetros de la pregunta que se encuentran
    # en `opciones`. Asumimos que el orden es aleatorio.
    orden = 'aleatorio'

    contador: int = 0
    linea: str
    lista: List[str]
    ignorar: bool = True
    while ignorar:
        linea = lsTexto[contador].strip()
        contador += 1
        ignorar = len(linea) == 0 or linea.startswith(Info.COMMENT)
    contador -= 1

    # Se lee el número de cifras significativas.
    cifras = __leer_cifras__(opciones)

    # Definiendo diccionario.
    dLocal: Dict[str, Any] = {**dParams, **DFunRandom, **DFunciones}

    # Se leen variables.
    if linea == Info.VARIABLES:
        contador = __leer_variables__(contador, lsTexto, dLocal, dParams)

    # Redefinimos el diccionario, eliminando las funciones que generan
    # números aleatorios.
    dLocal = {**dParams, **DFunciones}

    # Se lee la pregunta.
    contador, lista = __leer_pregunta__(contador, lsTexto, dLocal, cifras)

    # Se leen los items
    contador, litems = __items_unica__(contador, lsTexto, dLocal, cifras)

    # Se tiene que generar de nuevo la pregunta.
    if contador + len(litems) == 0:
        return latex_unica(opciones, lsTexto, dParams, revisar)

    if revisar:
        # Se obtiene cuáles items son respuesta correcta.
        litems = __respuestas_unica__(litems, opciones, dLocal)
        litems = [(tupla[0], '%s%s' % ('R/ ' if tupla[0] else '', tupla[1]))
                  for tupla in litems]

    # Desordenamos los items.
    if orden == 'aleatorio':
        if revisar:
            # Se llama a random.shuffle para mantener la semilla
            logging.debug('Random: fake')
            random.shuffle([*range(len(litems))])
        else:
            logging.debug('Random: Desordenando texto de items.')
            random.shuffle(litems)

    # Construimos el latex
    if columnas > 1:
        lista.append('    \\begin{multicols}{%d}\n'%columnas)
    lista.append('    \\begin{enumerate}%s\n' % Info.FORMATO_ITEM)
    for _, item in litems:
        lista.append('      \\item %s' % item)
    lista.append('    \\end{enumerate}\n')
    if columnas > 1:
        lista.append('    \\end{multicols}\n')
    return ('%s\n' % ''.join(lista).strip())


def latex_corta(opciones: str, lsTexto: List[str], dParams: Dict[str, Any],
                revisar: bool) -> str:
    """LaTeX de pregunta de respuesta corta.

    Argumentos
    ---------
    opciones:
        Primera línea. Para leer las opciones específicas.
    linea:
        Resto de las líneas de texto.
    dParams:
        Diccionario de variables definidas por el usuario.

    Devuelve
    --------
    Texto LaTeX de la pregunta, con los parámetros ya sustituidos.
    """

    logging.debug('Entrando a "latex_corta"')
    logging.debug('Texto: %s', ''.join(lsTexto))

    linea: str
    contador = 0
    # Aquí se guarda línea a línea de la pregunta.
    lista: List[str]

    # Se ignoran los comentarios.
    ignorar: bool = True
    while ignorar:
        linea = lsTexto[contador].strip()
        contador += 1
        ignorar = len(linea) == 0 or linea.startswith(Info.COMMENT)
    contador -= 1

    # Se lee el número de cifras significativas.
    cifras = __leer_cifras__(opciones)

    # Definiendo diccionario.
    dLocal: Dict[str, Any] = {**dParams, **DFunRandom, **DFunciones}

    # Se leen variables.
    if linea == Info.VARIABLES:
        contador = __leer_variables__(contador, lsTexto, dLocal, dParams)

    # Redefinimos el diccionario, eliminando las funciones que generan
    # números aleatorios.
    dLocal = {**dParams, **DFunciones}

    # Se lee la pregunta.
    contador, lista = __leer_pregunta__(contador, lsTexto, dLocal, cifras)

    if revisar:
        linea = lsTexto[contador].strip()
        contador += 1
        logging.debug('Respuesta corta -> Revisar: Imprimiendo respuesta')
        assert(linea.strip().startswith(Info.LITEM))
        ignorar = True
        while ignorar:
            linea = lsTexto[contador].strip()
            contador += 1
            ignorar = len(linea) == 0 or linea.startswith(Info.COMMENT)
        lista.append('\\bigskip\n\n\\noindent R/ %s\n'
                     % str(eval(linea, DGlobal, dLocal)))

    return ('%s\n' % ''.join(lista).strip())


def latex_encabezado(opciones: str, lsTexto: List[str],
                     dParams: Dict[str, Any]) -> str:
    """LaTeX de encabezado

    Argumentos
    ---------
    opciones:
        Primera línea. Para leer las opciones específicas.
    linea:
        Resto de las líneas de texto.
    dParams:
        Diccionario de variables definidas por el usuario.

    Devuelve
    --------
    Texto LaTeX del encabezado, con los parámetros ya sustituidos.
    """

    logging.debug('Entrando a "latex_encabezado"')
    logging.debug('Texto: %s', ''.join(lsTexto))

    linea: str
    contador = 0
    lista: List[str]
    # Se ignoran los comentarios.
    ignorar: bool = True
    while ignorar:
        linea = lsTexto[contador].strip()
        contador += 1
        ignorar = len(linea) == 0 or linea.startswith(Info.COMMENT)
    contador -= 1

    # Se lee el número de cifras significativas.
    cifras = __leer_cifras__(opciones)

    # Definiendo diccionario.
    dLocal: Dict[str, Any] = {**dParams, **DFunRandom, **DFunciones}

    # Se leen variables.
    if linea == Info.VARIABLES:
        contador = __leer_variables__(contador, lsTexto, dLocal, dParams)

    # Redefinimos el diccionario, eliminando las funciones que generan
    # números aleatorios.
    dLocal = {**dParams, **DFunciones}

    # Se lee la pregunta.
    contador, lista = __leer_pregunta__(contador, lsTexto, dLocal, cifras)

    return ('\n\\bigskip\n\n%s\n' % ''.join(lista).strip())


def respuesta_corta(opciones: str, lsTexto: List[str],
                    dParams: Dict[str, Any]) -> Respuesta:
    """Objeto Respuesta de pregunta de respuesta corta.

    Argumentos
    ---------
    opciones:
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

    logging.debug('Entrando a "respuesta_corta"')
    logging.debug('Texto: %s', ''.join(lsTexto))

    # Se inicializa el objeto Respuesta.
    resp = Respuesta(TPreg.RESP_CORTA)

    linea: str
    contador = 0
    # Se ignoran los comentarios.
    contador = __ignorar__(contador, lsTexto)

    # Definiendo diccionario.
    dLocal: Dict[str, Any] = {**dParams, **DFunRandom, **DFunciones}

    # Se leen variables.
    if lsTexto[contador].strip() == Info.VARIABLES:
        contador = __leer_variables__(contador, lsTexto, dLocal, dParams)

    # Deberíamos estar en la pregunta. Nos la brincamos, porque no se
    # debería de llamar a ninguna función random aquí.
    linea = lsTexto[contador].strip()
    contador += 1
    assert(linea == Info.PREGUNTA)
    linea = lsTexto[contador]
    contador += 1
    while not linea.strip().startswith(Info.LITEM):
        linea = lsTexto[contador]
        contador += 1

    # Redefinimos el diccionario, eliminando las funciones que generan
    # números aleatorios.
    dLocal = {**dParams, **DFunciones}

    # Ahora siguen los items.
    __items_corta__(contador - 1, lsTexto, resp, dLocal)

    return resp


def respuesta_unica(opciones: str, lsTexto: List[str],
                    dParams: Dict[str, Any]) -> Respuesta:
    """Objeto Respuesta de pregunta de selección única.

    Argumentos
    ---------
    opciones:
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
    logging.debug('Texto: %s', ''.join(lsTexto))

    # Creando el objeto de la respuesta.
    resp = Respuesta(TPreg.UNICA)

    # Extrayendo las opciones de la pregunta.
    # Primero el orden
    orden = __leer_orden__(opciones)

    contador: int = 0
    linea: str
    # Se ignoran los comentarios.
    contador = __ignorar__(contador, lsTexto)

    # Se define el diccionario.
    dLocal: Dict[str, Any] = {**dParams, **DFunRandom, **DFunciones}

    # Se leen las variables
    if lsTexto[contador].strip() == Info.VARIABLES:
        contador = __leer_variables__(contador, lsTexto, dLocal, dParams)

    # Deberíamos estar en la pregunta. Nos la brincamos, porque no se
    # debería de llamar a ninguna función random aquí.
    linea = lsTexto[contador].strip()
    contador += 1
    assert(linea == Info.PREGUNTA)
    linea = lsTexto[contador]
    contador += 1
    while not linea.strip().startswith(Info.LITEM):
        linea = lsTexto[contador]
        contador += 1

    # Generamos los items. No nos interesan las cifras?
    # TODO: Revisar el uso de cifras. Poner 0, gener\'o un error!!!
    contador, litems = __items_unica__(contador - 1, lsTexto, dLocal, 3)

    # Se obtiene cuáles items son respuesta correcta.
    litems = __respuestas_unica__(litems, opciones, dLocal)

    # Desordenamos los items.
    if orden == 'aleatorio':
        logging.debug('Random: Desordenando resp items.')
        resp.add_opcion(TPreg.ALEATORIO)
        random.shuffle(litems)
    if all([tupla[0] for tupla in litems]):
        resp.add_opcion(TPreg.TODOS)
    else:
        for i in range(len(litems)):
            if litems[i][0]:
                resp.add_respuesta(i)
    return resp


def respuesta_encabezado(opciones: str, lsTexto: List[str],
                         dParams: Dict[str, Any]) -> Respuesta:
    """Objeto Respuesta de encabezado.

    Argumentos
    ---------
    opciones:
        Primera línea. Para leer las opciones específicas.
    linea:
        Resto de las líneas de texto.
    dParams:
        Diccionario de variables definidas por el usuario.

    Devuelve
    --------
        Objeto de tipo Respuesta de Encabezado, con los parámetros ya
        sustituidos.
    """

    logging.debug('Entrando a "respuesta_encabezado"')
    logging.debug('Texto: %s', ''.join(lsTexto))

    # Se inicializa el objeto Respuesta.
    resp = Respuesta(TPreg.ENCABEZADO)

    # Se ignoran los comentarios.
    linea: str
    contador = 0
    ignorar = True
    while ignorar:
        linea = lsTexto[contador].strip()
        contador += 1
        ignorar = len(linea) == 0 or linea.startswith(Info.COMMENT)
    contador -= 1

    # Definiendo diccionario.
    dLocal: Dict[str, Any] = {**dParams, **DFunRandom, **DFunciones}

    # Se leen variables.
    if linea == Info.VARIABLES:
        contador = __leer_variables__(contador, lsTexto, dLocal, dParams)

    # No hay nada más que hacer por acá.
    return resp


def __leer_orden__(opciones: str) -> str:
    """ Lee tipo de orden de items en selección única.

    Argumentos
    ----------
    opciones:
        Texto de tipo.

    Devuelve
    --------
        El tipo de orden. Actualmente sólo se tiene `aleatorio`.
    """
    orden: str
    orden = parserPPP.derechaIgual(opciones, 'orden')
    if len(orden) == 0:
        orden = 'aleatorio'
    elif orden != 'aleatorio':
        logging.error('Tipo de orden desconocido: `%s`' % opciones)
    return orden


def __respuestas_unica__(litems: List[Item], opciones: str, dLocal):
    """ Cambia a True aquellos items cuya respuesta es la correcta.

    Todos los items se asume que vienen con False. Revisa en opciones
    cuales son los índices de las respuestas correctas, y cambia
    la tupla respectiva a True.

    Argumentos
    ----------
    litems:
        Lista de tuplas de la forma [(False, txt_item)].

    opciones:
        Opciones de la pregunta.
    """
    size = len(litems)

    algoSalioMal: str = parserPPP.derechaIgual(opciones, 'comodin').strip()
    opcion: str = ''
    if len(algoSalioMal):
        opcion = eval(algoSalioMal, DGlobal, dLocal)

    if len(opcion)==0:
        opcion = parserPPP.derechaIgual(opciones, 'opcion').strip()

    if opcion == 'todos':
        litems = [(True, tupla[1]) for tupla in litems]
    elif len(opcion) == 0:
        # La respuesta predeterminada.
        litems[0] = (True, litems[0][1])
    else:
        txts = opcion.split('&')
        for yo in txts:
            try:
                indice = int(yo)
            except ValueError:
                logging.error(
                        'No se pudo leer indice en opcion: `%s`' % opciones)
                continue
            if indice >= size:
                logging.error('Indice `%d` supera número de items `%d`.'
                              % (indice, size))
                logging.error('Recuerde que es 0-indexado!')
                continue
            litems[indice] = (True, litems[indice][1])
    return litems


def __items_unica__(contador: int, lsTexto: List[str], dLocal: Dict[str, Any],
                    cifras: int) -> Tuple[int, List[Item]]:
    """ Lee los items como [(False, txt_item)]

    Argumentos
    ----------
    contador:
        Índice actual de lsTexto.
    lsTexto:
        Lista de líneas de texto de la pregunta completa.
    dLocal:
        Diccionario de variables.

    Devuelve
    --------
        El contador actualizado y la lista de items.
    """
    texto: List[str] = []
    linea: str = lsTexto[contador]
    contador += 1
    assert(linea.strip().startswith(Info.LITEM))
    # TODO Hay que leer la opción de indice del item cuando
    # corresponda. Primero se va a crear una lista de los items.
    litems: List[Item] = []
    item: str
    ultimo: str
    while contador < len(lsTexto):
        linea = lsTexto[contador]
        contador += 1
        # Un nuevo item. Finalizamos el anterior.
        if linea.strip().startswith(Info.LITEM):
            # TODO falta revisar opciones como índice.
            # Se construye el texto del último item.
            ultimo = ' '.join(texto).strip().expandtabs(0)
            # Vamos a comparar el texto con los items anteriores para
            # ver si encontramos algo igual.
            for _, item in litems:
                if ultimo.replace(' ', '') == item.replace(' ', ''):
                    logging.debug('Generar de nuevo:')
                    logging.debug('  %s = %s!!' % (item, ultimo))
                    # Se tiene que generar de nuevo la pregunta.
                    return (0, [])
            litems.append((False, '%s\n\n' % ultimo))
            texto = []
        else:
            texto.append('%s' % parserPPP.update(linea, dLocal, cifras))

    # Falta agregar a la lista el último item
    litems.append((False, '%s\n\n' % ''.join(texto).rstrip()))
    return (contador, litems)


def __path_graphics__(filename: str, texto: str) -> str:
    """ Modifica el path de cada figura al path absoluto.

    Argumentos
    ----------
    filename:
        Path completo al archivo. De aquí se estrae la carpeta en la
        cual está.
    texto:
        Texto de la pregunta que se va a sustituir.
    """
    # Comenzamos extrayendo el path hasta el folder del archivo.
    path: str = os.path.dirname(filename)
    if len(path) > 0:
        path = os.path.join(path, '')
        # Ponemos el path en terminos absolutos.
        cwd = os.getcwd()
        os.chdir(path)
        # Aqu\'i vamos a permitir linux, porque es para generar
        # el archivo .tex.
        path = os.getcwd().replace('\\', '/')
        os.chdir(cwd)

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


def __leer_variables__(contador: int, lsTexto: List[str],
                       dLocal: Dict[str, Any], dParams: Dict[str, Any]) -> int:
    """ Se leen las variables de una pregunta.

    Argumentos
    ----------
    contador:
        Índice de la actual línea de texto.
    lsTexto:
        Líneas de texto de la pregunta.
    dLocal:
        Diccionario para evaluar las variables.
    dParams:
        Diccionario de las variables definidas por el usuario.

    Devuelve
    --------
        Evalúa las variables, las guarda en dParams, y devuelve el
        índice de la siguiente línea a trabajar.
    """
    linea = lsTexto[contador].strip()
    contador += 1
    while True:
        linea = lsTexto[contador].strip()
        contador += 1
        if linea == Info.PREGUNTA:
            break
        elif len(linea) == 0 or linea.startswith(Info.COMMENT):
            continue
        parserPPP.evaluarParam(linea, dLocal, dParams)
    return contador - 1


def __leer_pregunta__(contador: int, lsTexto: List[str],
                      dLocal: Dict[str, Any],
                      cifras: int) -> Tuple[int, List[str]]:
    """ Se lee el texto de la pregunta.

    Argumentos
    ----------
    contador:
        Índice de la actual línea de texto.
    lsTexto:
        Líneas de texto de la pregunta.
    dLocal:
        Diccionario para evaluar las variables.
    cifras:
        Cifras significativas para imprimir números en punto flotante.

    Devuelve
    --------
        Contador, y cada una de las líneas de la pregunta.
    """
    linea: str = lsTexto[contador].strip()
    contador += 1
    lista: List[str] = []
    assert(linea == Info.PREGUNTA)
    linea = lsTexto[contador]
    contador += 1
    texto: List[str] = []
    while not linea.strip().startswith(Info.LITEM):
        # Agregamos la línea de texto actualizando las @-expresiones.
        texto.append(parserPPP.update(linea, dLocal, cifras))
        if contador == len(lsTexto):
            break
        linea = lsTexto[contador]
        contador += 1
    lista.append('%s\n' % (''.join(texto).rstrip()))
    return (contador - 1, lista)


def __leer_cifras__(opciones: str) -> int:
    """ Lee número de cifras significativas. """
    # Definiendo el número de cifras significativas en 3.
    cifras: int = 3
    # Buscando si el usuario lo definió.
    texto: str = parserPPP.derechaIgual(opciones, 'cifras')
    if len(texto) > 0:
        try:
            cifras = int(texto)
        except ValueError:
            logging.error('No se pudo leer `cifras` en `%s`.' % opciones)
            logging.error('Se utilizan 3 de forma predeterminada.')
            cifras = 3
    return cifras


def __ignorar__(contador: int, lsTexto: List[str]) -> int:
    """ Ignora comentarios y líneas en blanco. """
    ignorar: bool = True
    linea: str
    while ignorar:
        linea = lsTexto[contador].strip()
        contador += 1
        ignorar = len(linea) == 0 or linea.startswith(Info.COMMENT)
    return contador - 1


def __items_corta__(contador: int, lsTexto: List[str], resp: Respuesta,
                    dLocal: Dict[str, Any]):
    """ Lee los items de las preguntas de respuesta corta. """
    valor: Numero
    error: float
    linea: str = lsTexto[contador]
    contador += 1
    assert(linea.strip().startswith(Info.LITEM))
    # Puede haber respuestas cortas con varias respuestas posibles de
    # tal manera que el radio del error aceptable se aumenta, y se
    # disminuye el factor del puntaje obtenido.
    while True:
        if linea.strip().startswith(Info.LITEM):
            linea = linea.strip(Info.STRIP)
            # Leyendo error
            error = __leer_float__(linea, 'error', 0.0)

            # Leyendo factor.
            factor = __leer_float__(linea, 'factor', 1.0)

            # Leyendo funcion.
            texto = parserPPP.derechaIgual(linea, 'funcion')
            if len(texto):
                logging.debug('variable de funcion = `%s`'%texto)
                try:
                    f = eval(texto, DGlobal, dLocal)
                    logging.debug('funcion = `%s`'%f)
                except:
                    logging.error('No se pudo evaluar funcion.')
                    f = None
            else:
                f = None

            # Ya se puede leer la siguiente línea y evaluar la
            # expresión.
            linea = lsTexto[contador].strip()
            contador += 1
            logging.debug('__items_corta__ evaluar: `%s`' % linea)
            valor = eval(linea, DGlobal, dLocal)
            resp.add_respuesta((valor, error, factor, f))
        if contador == len(lsTexto):
            break
        linea = lsTexto[contador]
        contador += 1


def __leer_float__(linea: str, etiqueta: str, default: float) -> float:
    """ Lee valor flotante en opcion.

    Argumentos
    ----------
    linea:
        Línea de texto.
    etiqueta:
        Etiqueta se se busca.
    default:
        Valor predeterminado, en caso de que no esté la etiqueta o no se
        pueda leer valor.

    Devuelve
    --------
        Valor leído o valor predeterminado en caso de que no se haya
        podido leer.
    """
    resp: float = default
    texto = parserPPP.derechaIgual(linea, etiqueta)
    if len(texto) > 0:
        try:
            resp = float(texto)
        except ValueError:
            logging.error('No se pudo leer %s: `%s`' % (etiqueta, linea))
    return resp
