import logging
from typing import List, Tuple

import Info
import parserPPP
from pregunta import Pregunta
from seccion import Seccion


def blancos(contador: int, lsTexto: List[str]) -> int:
    """ Se ignoran las líneas en blanco o comentarios.

    Argumentos
    ----------
    contador:
        Índice inicial.
    lsTexto:
        Texto de entrada como una lista, donde cada elemento es un
        renglón.

    Devuelve
    --------
    Índice de la siguiente línea que *no* es un comentario o una línea
    en blanco.
    """
    linea: str
    ignorar = True
    while ignorar:
        if contador >= len(lsTexto):
            return -1
        linea = lsTexto[contador].strip()
        contador += 1
        ignorar = len(linea) == 0 or linea.startswith(Info.COMMENT)
    return contador - 1


def unaLinea(contador: int, lsTexto: List[str],
             etiqueta: str) -> Tuple[int, str]:
    """ Se lee una línea según la etiqueta dada.

    Argumentos
    ----------
    contador:
        Índice inicial.
    lsTexto:
        Texto de entrada como una lista, donde cada elemento es un
        renglón.
    etiqueta:
        Etiqueta que se espera.

    Devuelve
    --------
    Una tupla formada por el contador en el valor que se debe seguir,
    y el texto solicitado en caso de que estuviera la etiqueta.
    """
    contador = blancos(contador, lsTexto)
    linea: str = lsTexto[contador].strip()
    contador += 1
    # No se encontró la etiqueta. Terminamos
    if linea != etiqueta:
        return contador - 1, ''
    contador = blancos(contador, lsTexto)
    linea = lsTexto[contador].strip()
    contador += 1
    return contador, linea


def variasLineas(contador: int, lsTexto: List[str],
                 etiqueta: str) -> Tuple[int, List[str]]:
    """ Se leen varias líneas según la etiqueta dada.

    Argumentos
    ----------
    contador:
        Índice inicial.
    lsTexto:
        Texto de entrada como una lista, donde cada elemento es un
        renglón.
    etiqueta:
        Etiqueta que se espera.

    Devuelve
    --------
    Una tupla formada por el contador en el valor que se debe seguir,
    y una lista con el texto solicitado en caso de que estuviera la
    etiqueta.
    """
    lista: List[str] = []
    contador = blancos(contador, lsTexto)
    linea: str = lsTexto[contador].strip()
    contador += 1
    # No se encontró la etiqueta. Terminamos
    if linea != etiqueta:
        return contador - 1, []
    while True:
        contador = blancos(contador, lsTexto)
        linea = lsTexto[contador].strip()
        contador += 1
        if linea.startswith(Info.ABRIR):
            break
        lista.append(linea)
    return contador - 1, lista


def verbatim(contador: int, lsTexto: List[str],
             etiqueta: str) -> Tuple[int, str]:
    """ Se lee verbatim el texto de la etiqueta dada.

    Argumentos
    ----------
    contador:
        Índice inicial.
    lsTexto:
        Texto de entrada como una lista, donde cada elemento es un
        renglón.
    etiqueta:
        Etiqueta que se espera.

    Devuelve
    --------
    Verbatim el texto de la etiqueta dada, hasta el inicio de la
    próxima etiqueta.
    """
    lista: List[str] = []
    contador = blancos(contador, lsTexto)
    linea: str = lsTexto[contador].strip()
    contador += 1
    # No se encontró la etiqueta. Terminamos
    if linea != etiqueta:
        return contador - 1, ''
    linea = lsTexto[contador]
    contador += 1
    while not linea.strip().startswith(Info.ABRIR):
        lista.append(linea)
        linea = lsTexto[contador]
        contador += 1
    linea = '%s\n' % ''.join(lista).strip()
    return contador - 1, linea


def secciones(contador: int, lsTexto: List[str],
              dirTrabajo: str) -> List[Seccion]:
    seccion: Seccion
    lista: List[Seccion] = []
    es_aleatorio: bool = False
    linea: str = lsTexto[contador]
    tempo: str
    contador += 1
    while linea.startswith(Info.LSECCION):
        linea = linea.strip(Info.STRIP)
        logging.info('Llamando a seccion ...')
        tempo = parserPPP.derechaIgual(linea, 'orden')
        es_aleatorio = tempo == 'aleatorio'
        tempo = parserPPP.derechaIgual(linea, 'alfinal')
        logging.debug('Se agrega algo? `%s`' % tempo)
        # Creando la nueva seccion.
        lista.append(Seccion(contador, lsTexto, dirTrabajo, 
                             es_aleatorio, tempo))

        linea = lsTexto[contador].strip()
        contador += 1
        while contador < len(lsTexto) and not linea.startswith(Info.LSECCION):
            linea = lsTexto[contador].strip()
            contador += 1
        if contador == len(lsTexto):
            break
    return lista


def preguntas(contador: int, lsTexto: List[str], dirTrabajo: str,
              aleatorio: bool) -> List[Pregunta]:
    lista: List[Pregunta] = []
    # Guardamos cada línea, hasta que encontremos la primera
    # línea en blanco: esto señala el final de la sección.
    texto: str
    puntos: float
    muestra: int
    linea: str
    origen: str
    # El usuario puede definir bloques, para no hacer página nueva.
    bloque: bool = False
    while contador < len(lsTexto):
        linea = lsTexto[contador].strip()
        contador += 1
        # Línea en blanco, terminamos.
        if len(linea) == 0:
            break
        # Si es un comentario, continuamos con la siguiente línea.
        if linea.startswith(Info.COMMENT):
            continue
        # Inicio de bloque. Solamente en caso de las preguntas no
        # estén en orden aleatorio.
        if linea == Info.INICIO_BLOQUE:
            assert(not bloque)
            logging.debug('Ingresando a un bloque')
            bloque = True
            continue
        if linea == Info.FIN_BLOQUE:
            assert(bloque)
            logging.debug('Fin de bloque')
            bloque = False
            # Modificamos la pregunta anterior, para avisar que es la
            # última pregunta.
            lista[-1].set_ultima()
            logging.info(
                    'Se modifica pregunta anterior: %s' % lista[-1].origen)
            continue

        # Puntos de la pregunta.
        puntos = __puntos__(linea)

        # Tamaño de la muestra.
        muestra = __muestra__(linea)

        # # de columnas para las opciones
        columnas = __columnas__(linea)

        # Origen de la pregunta.
        texto = parserPPP.derechaIgual(linea, 'origen')
        if len(texto) == 0:
            logging.error('No se pudo leer origen de pregunta en "%s"' % linea
                          + 'La pregunta no se pudo incluir.')
            continue
        origen = '%s%s' % (dirTrabajo, texto)
        lista.append(Pregunta(puntos, origen, muestra, bloque, columnas))
        # Es la primera pregunta de un bloque.
        if bloque and (len(lista) == 1 or lista[-2].es_ultima()
                       or not lista[-2].es_bloque()):
            lista[-1].set_primera()
        logging.info('Se agrega pregunta: %s' % origen)
    return lista


def __puntos__(linea: str) -> float:
    # Buscamos los puntos de la pregunta, el tamaño de la
    # muestra y el origen de la pregunta.
    puntos = 1
    texto = parserPPP.derechaIgual(linea, 'puntaje')
    if len(texto) > 0:
        try:
            puntos = float(texto)
        except ValueError:
            puntos = 1
            texto = '%s "%s".\n%s' % (
                    'No se pudo leer puntaje en', linea,
                    'Por defecto queda en 1 pt')
            logging.warning(texto)
    return puntos


def __muestra__(linea: str) -> int:
    muestra = 1
    texto = parserPPP.derechaIgual(linea, 'muestra')
    if len(texto) > 0:
        try:
            muestra = int(texto)
        except ValueError:
            muestra = 1
            texto = '%s "%s".\n%s' % (
                    'No se pudo leer tamaño de la muestra en', linea,
                    'Por defecto queda de tamaño 1')
            logging.warning(texto)
    return muestra


def __columnas__(linea: str) -> int:
    columnas = 1
    texto = parserPPP.derechaIgual(linea, 'columnas')
    if len(texto) > 0:
        try:
            columnas = int(texto)
        except ValueError:
            columnas = 1
            texto = '%s "%s".\n%s' % (
                    'No se pudo leer número de columnas en', linea,
                    'Por defecto queda de 1 columna.')
            logging.warning(texto)
    return columnas
