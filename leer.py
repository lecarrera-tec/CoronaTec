import logging
from typing import List, Tuple

import Info
import parserPPP
from pregunta import Pregunta
from seccion import Seccion

# TODO ¿Ser\'a posible estandarizar todas las funciones en una sola?


def blancos(lsTexto: List[str]) -> str:
    """ Se ignoran las líneas en blanco o comentarios.

    Argumentos
    ----------
    lsTexto:
        Texto de entrada como una lista, donde cada elemento es un
        renglón.

    Devuelve
    --------
    Un texto con la primera línea que *no* es un comentario o una línea
    en blanco.
    """
    linea: str
    ignorar = True
    while ignorar:
        linea = lsTexto.pop(0).strip()
        ignorar = len(linea) == 0 or linea[0] == Info.COMMENT
    return linea


def escuelas(linea: str, lsTexto: List[str]) -> Tuple[List[str], str]:
    """ Se leen las escuelas participantes.

    Argumentos
    ----------
    lsTexto:
        Texto de entrada como una lista, donde cada elemento es un
        renglón.

    Devuelve
    --------
    Una lista con cada una de las escuelas.
    """
    assert(linea == Info.ESCUELAS)
    escuelas: List[str] = []
    while True:
        linea = blancos(lsTexto)
        if linea[0] == '<':
            break
        escuelas.append(linea)
    return escuelas, linea


def semestre(linea: str, lsTexto: List[str]) -> Tuple[str, str]:
    """ Se lee el semestre y el año.

    Argumentos
    ----------
    lsTexto:
        Texto de entrada como una lista, donde cada elemento es un
        renglón.

    Devuelve
    --------
    Texto del semestre y año.
    """
    assert(linea == Info.SEMESTRE)
    linea = blancos(lsTexto)
    return linea, blancos(lsTexto)


def tiempo(linea: str, lsTexto: List[str]) -> Tuple[str, str]:
    """ Se lee el tiempo asignado al examen.

    Argumentos
    ----------
    lsTexto:
        Texto de entrada como una lista, donde cada elemento es un
        renglón.

    Devuelve
    --------
    El tiempo ingresado por el usuario.
    """
    assert(linea == Info.TIEMPO)
    linea = blancos(lsTexto)
    return linea, blancos(lsTexto)


def cursos(linea: str, lsTexto: List[str]) -> Tuple[List[str], str]:
    """ Se lee los cursos para los cuales aplica el examen.

    Argumentos
    ----------
    lsTexto:
        Texto de entrada como una lista, donde cada elemento es un
        renglón.

    Devuelve
    --------
    Una lista con cada uno de los cursos.
    """
    assert(linea == Info.CURSOS)
    # Agregamos todas las líneas que no comiencen con comentario
    # hasta llegar a una línea en blanco.
    lista: List[str] = []
    linea = blancos(lsTexto)
    while not linea[0] == '<':
        lista.append(linea)
        linea = blancos(lsTexto)
    return lista, linea


def titulo(linea: str, lsTexto: List[str]) -> Tuple[str, str]:
    """ Se lee el título del examen o de la sección. Puede ser opcional.

    Si no tiene título, entonces se devuelve el título en blanco y la
    línea de texto original, porque tiene la siguiente etiqueta.

    Argumentos
    ----------
    lsTexto:
        Texto de entrada como una lista, donde cada elemento es un
        renglón.

    Devuelve
    --------
    Una tupla con el título (si había) y la siguiente línea de texto.
    """
    if linea == Info.TITULO:
        resp = blancos(lsTexto)
        linea = blancos(lsTexto)
    else:
        resp = ''
    return (resp, linea)


def encabezado(linea: str, lsTexto: List[str]) -> Tuple[str, str]:
    """ Se lee el encabezado de LaTeX para el examen. Es opcional.

    Argumentos
    ----------
    lsTexto:
        Texto de entrada como una lista, donde cada elemento es un
        renglón.

    Devuelve
    --------
    El encabezado y la siguiente línea de texto.
    """
    lista: List[str] = []
    if linea == Info.ENCABEZADO:
        linea = lsTexto.pop(0)
        while linea.find(Info.ABRIR) == -1:
            lista.append(linea)
            linea = lsTexto.pop(0)
        resp = '%s\n' % ''.join(lista).strip()
    else:
        resp = ''
    return (resp, linea.strip())


def instrucciones(linea: str, lsTexto: List[str]) -> Tuple[str, str]:
    # Revisamos si son las instrucciones. Pueden abarcar varias
    # líneas de texto. Si no hubiera instrucciones, observe que
    # entonces la variable estaría en blanco.
    lista: List[str] = []
    if linea.strip() == Info.INSTRUCCIONES:
        linea = lsTexto.pop(0)
        while linea.find(Info.ABRIR) == -1:
            lista.append(linea)
            linea = lsTexto.pop(0)
        resp = '%s\n' % ''.join(lista).strip()
    else:
        resp = ''
    return (resp, linea.strip())


def secciones(linea: str, lsTexto: List[str],
              dirTrabajo: str) -> List[Seccion]:
    # No queda de otra. Tienen que seguir las secciones. Una lista
    # de instancias de la clase Seccion.
    counter: int = 0
    respuesta: List[Seccion] = []
    es_aleatorio: bool = False
    while linea.startswith(Info.LSECCION):
        linea = linea.strip(Info.STRIP)
        counter += 1
        logging.info('%d: Llamando a seccion ...' % counter)
        linea = parserPPP.derechaIgual(linea, 'orden')
        es_aleatorio = linea == 'aleatorio'
        # Creando la nueva seccion.
        respuesta.append(Seccion(lsTexto, dirTrabajo, es_aleatorio))
        if len(lsTexto) == 0:
            break
        linea = lsTexto.pop(0).strip()
    return respuesta


def preguntas(lsTexto: List[str], dirTrabajo: str,
              aleatorio: bool) -> List[Pregunta]:
    lista: List[Pregunta] = []
    # Guardamos cada línea, hasta que encontremos la primera
    # línea en blanco: esto señala el final de la sección.
    texto: str
    puntos: int
    muestra: int
    linea: str
    origen: str
    # El usuario puede definir bloques, para no hacer página nueva.
    bloque: bool = False
    while len(lsTexto) > 0:
        linea = lsTexto.pop(0).strip()
        # Línea en blanco, terminamos.
        if len(linea) == 0:
            break
        # Si es un comentario, continuamos con la siguiente línea.
        if linea[0] == Info.COMMENT:
            continue
        # Inicio de bloque. Solamente en caso de las preguntas no
        # estén en orden aleatorio.
        if linea == Info.INICIO_BLOQUE:
            assert(not bloque)
            assert(not aleatorio)
            bloque = True
            continue
        elif linea == Info.FIN_BLOQUE:
            assert(bloque)
            bloque = False
            # Modificamos la pregunta anterior, para avisar que es la
            # \'ultima pregunta.
            lista[-1].set_ultima()
            logging.info(
                    'Se modifica pregunta anterior: %s' % str(lista[-1]))
            continue

        # Puntos de la pregunta.
        puntos = __puntos__(linea)

        # Tamaño de la muestra.
        muestra = __muestra__(linea)

        # Origen de la pregunta.
        texto = parserPPP.derechaIgual(linea, 'origen')
        if len(texto) == 0:
            texto = '%s "%s".\n%s' % (
                    'No se pudo leer origen de pregunta en', linea,
                    'La pregunta no se pudo incluir.')
            logging.error(texto)
            continue
        origen = '%s%s' % (dirTrabajo, texto)
        lista.append(Pregunta(puntos, origen, muestra, bloque))
        # Es la primera pregunta de un bloque.
        if bloque and (len(lista) == 1 or lista[-2].es_ultima()
                        or not lista[-2].es_bloque()):
            lista[-1].set_primera()
        logging.info('Se agrega pregunta: %s' % origen)
    return lista


def __puntos__(linea: str) -> int:
    # Buscamos los puntos de la pregunta, el tamaño de la
    # muestra y el origen de la pregunta.
    puntos = 1
    texto = parserPPP.derechaIgual(linea, 'puntaje')
    if len(texto) > 0:
        try:
            puntos = int(texto)
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
