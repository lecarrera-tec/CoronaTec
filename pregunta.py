"""Leer archivos de preguntas."""

import logging
import os
import random
import sys
from typing import Any, List, Dict

import parserPPP
import Info
import TPreg
from respuesta import Respuesta
from diccionarios import DFunRandom, DFunciones, DGlobal

def get_latex(filename: str, dParams: Dict[str, Any], 
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
        Para especificar que se est\'a en la opci\'on de visualizar, y que 
        se debe especificar/imprimir la respuesta.

    Devuelve
    --------
    El texto LaTeX de la pregunta.
    """
    try:
        f = open(filename)
    except:
        logging.error('No se pudo abrir archivo "%s"' % filename) 
        return ''

    # Se obtienen todas las lineas del archivo y se cierra.
    lineas: List[str] = f.readlines()
    f.close()
    texto: str
    linea: str

    # Se ignoran los comentarios.
    ignorar: bool = True
    while ignorar:
        linea = lineas.pop(0).strip()
        ignorar = len(linea) == 0 or linea[0] == Info.COMMENT

    # Debe comenzar con el tipo de la pregunta. Leemos cuál es.
    assert(linea.startswith(Info.LTIPO))
    linea = linea.strip(Info.STRIP)
    tipo: str = parserPPP.derechaIgual(linea, 'tipo')
    if tipo == 'respuesta corta':
        texto = latex_corta(linea, lineas, dParams, revisar)
    elif tipo == 'seleccion unica':
        texto = latex_unica(linea, lineas, dParams, revisar)
    elif tipo == 'encabezado':
        texto = latex_encabezado(linea, lineas, dParams)

    # Queda aún algo muy importante por hacer, y es modificar el path 
    # de las figuras que se incluyan: \includegraphics[opciones]{path}
    # Primero comenzamos extrayendo el path hasta el folder donde está
    # el archivo.
    idx: int = filename.rfind('/')
    if idx > 0:
        path: str = filename[:idx]
        # Ponemos el path en terminos absolutos.
        cwd = os.getcwd()
        os.chdir(path)
        path = os.getcwd()
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

def latex_unica(opciones: str, lineas: List[str], 
                dParams: Dict[str, Any], revisar: bool) -> str:
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
        Para especificar que se est\'a en la opci\'on de visualizar, y que 
        se debe especificar/imprimir la respuesta.

    Devuelve
    --------
    Texto LaTeX de la pregunta, con los parámetros ya sustituidos.
    """

    logging.debug('Entrando a "latex_unica"')
    logging.debug('Texto : %s', ''.join(lineas))

    # TODO Faltan leer los parámetros de la pregunta que se encuentran
    # en `opciones`. Asumimos que el orden es aleatorio.
    orden = 'aleatorio'

    # El índice de la opción.
    opcion: str = parserPPP.derechaIgual(opciones, 'opcion')
    indice: int = 0
    if opcion == 'todos':
        None
    elif len(opcion) > 0:
        try:
            indice = int(opcion)
        except:
            logging.error('No se pudo leer el indice de la opcion: `%s`' 
                          % opcion)

    counter: int = 0
    linea: str
    lista: List[str] = []
    ignorar: bool = True
    while ignorar:
        linea = lineas[counter].strip(); counter += 1
        ignorar = len(linea) == 0 or linea[0] == Info.COMMENT
    # Definiendo diccionario.
    dLocal: Dict[str, Any] = {**dParams, **DFunRandom, **DFunciones}
    if linea == Info.VARIABLES:
        while True:
            linea = lineas[counter].strip(); counter += 1
            if linea == Info.PREGUNTA:
                break
            elif len(linea) == 0 or linea[0] == Info.COMMENT:
                continue
            parserPPP.evaluarParam(linea, dLocal, dParams)

    # Deberíamos estar en la pregunta. Hay que buscar si se necesitan
    # variables.
    assert(linea == Info.PREGUNTA)
    # Redefinimos el diccionario, eliminando las preguntas que generan
    # números aleatorios.
    dLocal = {**dParams, **DFunciones}
    linea = lineas[counter]; counter += 1
    texto: List[str] = []
    while not linea.strip().startswith(Info.LITEM):
        # Agregamos la línea de texto actualizando las @-expresiones.
        texto.append('    %s' % parserPPP.update(linea, dLocal))
        linea = lineas[counter]; counter += 1
    lista.append('%s\n%s' % (''.join(texto).rstrip(), '    \\nopagebreak\n'))

    # Ahora siguen los items.
    texto = []
    assert(linea.strip().startswith(Info.LITEM))
    # TODO Hay que leer la opción de indice del item cuando 
    # corresponda. Primero se va a crear una lista de los items.
    litems: List[str] = []
    item: str
    ultimo: str
    while counter < len(lineas):
        linea = lineas[counter]; counter += 1
        # Un nuevo item. Finalizamos el anterior.
        if linea.strip().startswith(Info.LITEM):
            # TODO falta revisar opciones como índice.
            # Se construye el texto del \'ultimo item.
            ultimo = ' '.join(texto).strip().expandtabs(0)
            # Vamos a comparar el texto con los items anteriores para
            # ver si encontramos algo igual.
            for item in litems:
                if ultimo.replace(' ', '') == item.replace(' ', ''):
                    logging.debug('Generar de nuevo:')
                    logging.debug('  %s = %s!!' % (item, ultimo))
                    # Se tiene que generar de nuevo la pregunta.
                    return latex_unica(opciones, lineas, dParams, revisar)
            litems.append('%s\n\n' % ultimo)
            texto = []
        else:
            texto.append('%s' % parserPPP.update(linea, dLocal))

    # Falta agregar a la lista el último item
    litems.append('%s\n\n' % ''.join(texto).rstrip())
    assert(indice < len(litems))
    if revisar:
        litems[indice] = 'R/ %s' % litems[indice]

    # Desordenamos los items.
    elif orden == 'aleatorio':
        random.shuffle(litems)
    # Construimos el latex
    lista.append('    \\begin{enumerate}%s\n' % Info.FORMATO_ITEM)
    for item in litems:
        lista.append('      \\item %s' % item)
    lista.append('    \\end{enumerate}\n')
    return ('%s\n' % ''.join(lista).strip())

def latex_corta(opciones: str, lineas: List[str], dParams: Dict[str, Any], 
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
    cifras:
        Número de cifras significativas a utilizar.

    Devuelve
    --------
    Texto LaTeX de la pregunta, con los parámetros ya sustituidos.
    """

    logging.debug('Entrando a "latex_corta"')
    logging.debug('Texto : %s', ''.join(lineas))

    # Definiendo el número de cifras significativas en 3.
    cifras: int = 3
    # Buscando si el usuario lo definió.
    texto: str = parserPPP.derechaIgual(opciones, 'cifras')
    if len(texto) > 0:
        try:
            cifras = int(texto)
        except:
            logging.error('No se pudo leer `cifras` en `%s`.' % opciones)
            logging.error('Se utilizan 3 de forma predeterminada.')
            cifras = 3

    # Aquí se guarda línea a línea de la pregunta.
    linea: str
    lista: List[str] = []

    # Se ignoran los comentarios.
    ignorar: bool = True
    while ignorar:
        linea = lineas.pop(0).strip()
        ignorar = len(linea) == 0 or linea[0] == Info.COMMENT

    # Definiendo diccionario y se evalúan las variables.
    dLocal: Dict[str, Any] = {**dParams, **DFunRandom, **DFunciones}
    if linea == Info.VARIABLES:
        while True:
            linea = lineas.pop(0).strip()
            if linea == Info.PREGUNTA:
                break
            elif len(linea) == 0 or linea[0] == Info.COMMENT:
                continue
            parserPPP.evaluarParam(linea, dLocal, dParams)

    # Deberíamos estar en la pregunta. Hay que buscar si se necesitan
    # variables.
    assert(linea == Info.PREGUNTA)
    # Redefinimos el diccionario, eliminando las preguntas que generan
    # números aleatorios.
    dLocal = {**dParams, **DFunciones}
    linea = lineas.pop(0)
    ltexto: List[str] = []
    while not linea.strip().startswith(Info.LITEM):
        # Se agrega la línea de texto actualizando las @-expresiones.
        ltexto.append('    %s' % parserPPP.update(linea, dLocal, cifras))
        linea = lineas.pop(0)
    lista.append('%s\n\n' % ''.join(ltexto).rstrip())

    if revisar:
        logging.debug('Respuesta corta -> Revisar: Imprimiendo respuesta')
        assert(linea.strip().startswith(Info.LITEM))
        ignorar = True
        while ignorar:
            linea = lineas.pop(0).strip()
            ignorar = len(linea) == 0 or linea[0] == Info.COMMENT
        lista.append('\\bigskip\n\n\\noindent R/ %s\n' 
                     % str(eval(linea, DGlobal, dLocal)))

    return ('%s\n' % ''.join(lista).strip())

def latex_encabezado(opciones: str, lineas: List[str], 
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
    cifras:
        Número de cifras significativas a utilizar.

    Devuelve
    --------
    Texto LaTeX del encabezado, con los parámetros ya sustituidos.
    """

    logging.debug('Entrando a "latex_encabezado"')
    logging.debug('Texto : %s', ''.join(lineas))

    # Definiendo el número de cifras significativas en 3.
    cifras: int = 3
    # Buscando si el usuario lo definió.
    texto: str = parserPPP.derechaIgual(opciones, 'cifras')
    if len(texto) > 0:
        try:
            cifras = int(texto)
        except:
            logging.error('No se pudo leer `cifras` en `%s`.' % opciones)
            logging.error('Se utilizan 3 de forma predeterminada.')
            cifras = 3

    linea: str
    # Se ignoran los comentarios.
    ignorar: bool = True
    while ignorar:
        linea = lineas.pop(0).strip()
        ignorar = len(linea) == 0 or linea[0] == Info.COMMENT
    # Definiendo diccionario y se evalúan las variables.
    dLocal: Dict[str, Any] = {**dParams, **DFunRandom, **DFunciones}
    if linea == Info.VARIABLES:
        while True:
            linea = lineas.pop(0).strip()
            if linea == Info.PREGUNTA:
                break
            elif len(linea) == 0 or linea[0] == Info.COMMENT:
                continue
            parserPPP.evaluarParam(linea, dLocal, dParams)

    # Deberíamos estar en el encabezado. Hay que buscar si se necesitan
    # variables.
    assert(linea == Info.PREGUNTA)
    # Redefinimos el diccionario, eliminando las preguntas que generan
    # números aleatorios.
    dLocal = {**dParams, **DFunciones}
    ltexto: List[str] = []
    while len(lineas) > 0:
        linea = lineas.pop(0)
        # Se agrega la línea de texto actualizando las @-expresiones.
        ltexto.append('    %s' % parserPPP.update(linea, dLocal, cifras))
    return ('%s\n' % ''.join(ltexto).strip())

def get_respuesta(filename: str, dParams: Dict[str, Any]) -> Respuesta:
    """ Constructor de la respuesta.

    Lo que hace es clasificar el tipo de pregunta, y llamar a la función 
    correspondiente.

    Argumentos
    ----------
    filename:
        Nombre del archivo donde se encuentra la pregunta.
    dParams:
        Diccionario de los parámetros definidos por el usuario.

    Devuelve
    --------
        Objeto de tipo Respuesta de la pregunta, con los parámetros ya 
        sustituidos.
    """

    # Se abre el archivo, se leen y guardan las líneas y se cierra
    # el archivo.
    try:
        f = open(filename)
    except:
        logging.error('No se pudo abrir archivo "%s"' % filename) 
        sys.exit()
    lineas: List[str] = f.readlines()
    f.close()

    # Ignorando comentarios y líneas en blanco.
    ignorar: bool = True
    while ignorar:
        linea: str = lineas.pop(0).strip()
        ignorar = len(linea) == 0 or linea[0] == Info.COMMENT

    # Debe comenzar con el tipo de la pregunta. Leemos cuál es.
    assert(linea.startswith(Info.LTIPO))
    linea = linea.strip(Info.STRIP)
    tipo: str = parserPPP.derechaIgual(linea, 'tipo')
    if tipo == 'respuesta corta':
        return respuesta_corta(linea, lineas, dParams)
    elif tipo == 'seleccion unica':
        return respuesta_unica(linea, lineas, dParams)
    elif tipo == 'encabezado':
        return respuesta_encabezado(linea, lineas, dParams)

    logging.error('Tipo de pregunta desconocido: %s' % linea)
    return Respuesta(TPreg.NINGUNA)

def respuesta_corta(opciones: str, lineas: List[str], 
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
    logging.debug('Texto : %s', ''.join(lineas))

    # Se inicializa el objeto Respuesta.
    resp = Respuesta(TPreg.RESP_CORTA)

    # Definiendo el número de cifras significativas en 3.
    cifras: int = 3
    # Buscando si el usuario lo definió.
    texto: str = parserPPP.derechaIgual(opciones, 'cifras')
    if len(texto) > 0:
        try:
            cifras = int(texto)
        except:
            logging.error('No se pudo leer `cifras` en `%s`.' % opciones)

    # Ver si la respuesta es un entero, o de tipo flotante. El tipo
    # entero es el predeterminado.
    texto = parserPPP.derechaIgual(opciones, 'respuesta')
    esEntero: bool
    if len(texto) == 0 or texto == 'entero':
        esEntero = True
        resp.add_opcion(TPreg.ENTERO)
    elif texto == 'flotante':
        esEntero = False
        resp.add_opcion(TPreg.FLOTANTE)
    else:
        logging.critical('Tipo de respuesta desconocido: `%s`', texto)
        esEntero = True
        resp.add_opcion(TPreg.ENTERO)

    linea: str
    # Se ignoran los comentarios.
    ignorar: bool = True
    while ignorar:
        linea = lineas.pop(0).strip()
        ignorar = len(linea) == 0 or linea[0] == Info.COMMENT

    # Se leen los parámetros.
    dLocal: Dict[str, Any] = {**dParams, **DFunRandom, **DFunciones}
    if linea == Info.VARIABLES:
        while True:
            linea = lineas.pop(0).strip()
            if linea == Info.PREGUNTA:
                break
            elif len(linea) == 0 or linea[0] == Info.COMMENT:
                continue
            else:
                parserPPP.evaluarParam(linea, dLocal, dParams)

    # Deberíamos estar en la pregunta. Nos la brincamos, porque no se
    # debería de llamar a ninguna función random aquí.
    assert(linea == Info.PREGUNTA)
    linea = lineas.pop(0)
    while not linea.strip().startswith(Info.LITEM):
        linea = lineas.pop(0)

    # Ahora siguen los items.
    entero: int
    flotante: float
    error: float
    # Se redefine el diccionario para eliminar las funciones random.
    dLocal = {**dParams, **DFunciones}
    assert(linea.strip().startswith(Info.LITEM))
    # Puede haber respuestas cortas con varias respuestas posibles de 
    # tal manera que el radio del error aceptable se aumenta, y se
    # disminuye el factor del puntaje obtenido.
    while True:
        if linea.strip().startswith(Info.LITEM):
            linea = linea.strip(Info.STRIP)
            if esEntero:
                # No hay que leer opciones. Se obtiene la siguiente
                # línea y se lee la expresión.
                linea = lineas.pop(0).strip()
                try:
                    entero = eval(linea, DGlobal, dLocal)
                except:
                    logging.error('No se pudo evaluar expresion: `%s`' % linea)
                    entero = 0
                resp.add_respuesta(entero)
            else:
                # Es de tipo flotante. Hay que leer error aceptable y
                # factor del puntaje.
                texto = parserPPP.derechaIgual(linea, 'error')
                try:
                    error = float(texto)
                except:
                    logging.error('No se pudo leer error: `%s`' % linea)
                    error = 0.01
                texto = parserPPP.derechaIgual(linea, 'factor')
                if len(texto) == 0:
                    factor = 1.0
                else:
                    try:
                        factor = float(texto)
                    except:
                        logging.error('No se pudo leer factor: `%s`' % linea)
                        factor = 1.0
                # Ya se puede leer la siguiente línea y evaluar la 
                # expresión.
                linea = lineas.pop(0).strip()
                try:
                    flotante = eval(linea, DGlobal, dLocal)
                except:
                    logging.error('No se pudo evaluar expresion: `%s`' % linea)
                    flotante = 0.0
                resp.add_respuesta((flotante, error, factor))
        if len(lineas) == 0:
            break
        linea = lineas.pop(0)
    return resp

def respuesta_unica(opciones: str, lineas: List[str], 
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
    logging.debug('Texto : %s', ''.join(lineas))
    
    # Creando el objeto de la respuesta.
    resp = Respuesta(TPreg.UNICA)

    # Extrayendo las opciones de la pregunta.
    # Primero el orden
    orden = parserPPP.derechaIgual(opciones, 'orden')
    if len(orden) == 0:
        orden = 'aleatorio'
    elif orden != 'aleatorio':
        logging.error('Tipo de orden desconocido: `%s`' % opciones)

    # El índice de la opción.
    opcion: str = parserPPP.derechaIgual(opciones, 'opcion')
    indice: int = 0
    if opcion == 'todos':
        resp.add_opcion(TPreg.TODOS)
        # Aunque podríamos terminar acá, se necesitan leer las
        # variables y reordenar los items, porque sino cambiaríamos la 
        # semilla del aleatorio para el resto de las preguntas.
    elif len(opcion) > 0:
        try:
            indice = int(opcion)
        except:
            logging.error('No se pudo leer el indice de la opcion: `%s`' 
                          % opciones)

    # Se ignoran los comentarios.
    counter: int = 0
    linea: str
    ignorar: bool = True
    while ignorar:
        linea = lineas[counter].strip(); counter += 1
        ignorar = len(linea) == 0 or linea[0] == Info.COMMENT
    dLocal: Dict[str, Any] = {**dParams, **DFunRandom, **DFunciones}

    # Se leen las variables
    if linea == Info.VARIABLES:
        while True:
            linea = lineas[counter].strip(); counter += 1
            if linea == Info.PREGUNTA:
                break
            elif len(linea) == 0 or linea[0] == Info.COMMENT:
                continue
            else:
                parserPPP.evaluarParam(linea, dLocal, dParams)

    # Deberíamos estar en la pregunta. Nos la brincamos, porque no se
    # debería de llamar a ninguna función random aquí.
    assert(linea == Info.PREGUNTA)
    linea = lineas[counter]; counter += 1
    while not linea.strip().startswith(Info.LITEM):
        linea = lineas[counter]; counter += 1

    # Ahora siguen los items. Se tienen que construir para asegurarse de
    # que no hayan distractores repetidos, pero en realidad lo \'unico que
    # nos interesan son los \'indices.
    texto: str = []
    assert(linea.strip().startswith(Info.LITEM))
    # TODO Hay que leer la opción de indice del item cuando 
    # corresponda. Primero se va a crear una lista de los items.
    litems: List[str] = []
    indices: List[int] = [0]
    item: str
    ultimo: str
    while counter < len(lineas):
        linea = lineas[counter]; counter += 1
        # Un nuevo item. Finalizamos el anterior.
        if linea.strip().startswith(Info.LITEM):
            # Se agrega un \'indice, lo importante!
            indices.append(indices[-1] + 1)
            # TODO falta revisar opciones como índice.
            # Se construye el texto del \'ultimo item.
            ultimo = ' '.join(texto).strip().expandtabs(0)
            # Vamos a comparar el texto con los items anteriores para
            # ver si encontramos algo igual.
            for item in litems:
                if ultimo.replace(' ', '') == item.replace(' ', ''):
                    logging.debug('Generar de nuevo:')
                    logging.debug('  %s = %s!!' % (item, ultimo))
                    # Se tiene que generar de nuevo la respuesta.
                    return respuesta_unica(opciones, lineas, dParams, revisar)
            litems.append('%s\n\n' % ultimo)
            texto = []
        else:
            texto.append('%s' % parserPPP.update(linea, dLocal))

    # Desordenamos los items.
    if orden == 'aleatorio':
        resp.add_opcion(TPreg.ALEATORIO)
        random.shuffle(indices)
    resp.add_respuesta(indices.index(indice))
    return resp

def respuesta_encabezado(opciones: str, lineas: List[str], 
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
    logging.debug('Texto : %s', ''.join(lineas))

    # Se inicializa el objeto Respuesta.
    resp = Respuesta(TPreg.ENCABEZADO)

    # Definiendo el número de cifras significativas en 3.
    cifras: int = 3
    # Buscando si el usuario lo definió.
    texto: str = parserPPP.derechaIgual(opciones, 'cifras')
    if len(texto) > 0:
        try:
            cifras = int(texto)
        except:
            logging.error('No se pudo leer `cifras` en `%s`.' % opciones)

    linea: str
    # Se ignoran los comentarios.
    ignorar: bool = True
    while ignorar:
        linea = lineas.pop(0).strip()
        ignorar = len(linea) == 0 or linea[0] == Info.COMMENT

    # Se leen los parámetros.
    dLocal: Dict[str, Any] = {**dParams, **DFunRandom, **DFunciones}
    if linea == Info.VARIABLES:
        while True:
            linea = lineas.pop(0).strip()
            if linea == Info.PREGUNTA:
                break
            elif len(linea) == 0 or linea[0] == Info.COMMENT:
                continue
            else:
                parserPPP.evaluarParam(linea, dLocal, dParams)

    # No hay nada más que hacer por acá.
    return resp
