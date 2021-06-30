import logging
import os
import random
from typing import Any, Dict, List, Union
import sys

import Info
import leer
import pregunta
from pregunta import Pregunta
import TPreg
from respuesta import Respuesta

# TODO Revisar errores mientras se leen los archivos, manejar
# excepciones e informar al usario utilizando logging.

Latex = Union[str, List[str]]
Resps = Union[Respuesta, List[Respuesta]]


class Seccion:
    """Parseado de sección de pruebas de preguntas parametrizadas.

    Atributos
    ---------
    aleatorias: bool
        Si las preguntas se quieren (o no) en orden aleatorio. El
        predeterminado es que no.
    instrucciones: str
        Texto de las instrucciones específicas de la sección.
    preguntas: List[Pregunta]
        Una lista de tuplas. La información de la tupla corresponde
        al puntaje de la pregunta, el path, el número de muestras que se
        extrae en caso de que sea una carpeta, y si está contenida en
        un bloque o no.
    puntaje: int
        Puntaje total de la sección.
    titulo: str
        El título de la sección.
    """
    def __init__(
            self, contador: int, lsTexto: List[str], dirTrabajo: str,
            aleatorio: bool = False):
        """Constructor a partir de archivo y el orden de las preguntas.

        Se supone que la última línea que se leyó del archivo es
        justamente la etiqueta para la sección, y por eso estamos acá.

        Aquí se definen:
          - titulo: titulo de la sección, si tiene.
          - instrucciones: si son dadas por el usuario.
          - puntaje: puntaje total de la sección
          - preguntas: tuplas [int, str, int], formadas por el puntaje,
                       el origen y el tamaño de la muestra de la
                       pregunta.
          - aleatorias: Si el orden de las preguntas debe ser aleatorio
                        o no.
        """
        self.puntaje: int = 0
        self.aleatorias: bool = aleatorio

        linea: str
        # Se busca un título
        self.titulo: str
        contador, self.titulo = leer.unaLinea(contador, lsTexto, Info.TITULO)
        if len(self.titulo) > 0:
            logging.info('<Titulo>: %s' % self.titulo)
        else:
            logging.info('No hay titulo en la sección.')

        # Se buscan instrucciones.
        self.instrucciones: str
        contador, self.instrucciones = leer.verbatim(contador, lsTexto,
                                                     Info.INSTRUCCIONES)
        if len(self.instrucciones) > 0:
            logging.info('<Instrucciones>: %s' % self.instrucciones)
        else:
            logging.info('No hay instrucciones en la sección.')

        # Deberían de seguir las direcciones a los archivos de las
        # preguntas.
        linea = lsTexto[contador]
        contador += 1
        assert(linea.strip().startswith(Info.PREGUNTAS))
        # Vamos a guardar una lista de tuplas, donde el primer
        # elemento es el puntaje, y el segundo la dirección.
        self.preguntas: List[Pregunta]
        self.preguntas = leer.preguntas(contador, lsTexto, dirTrabajo,
                                        aleatorio)

    def get_puntaje(self) -> int:
        """Devuelve el puntaje total de la sección."""
        if self.puntaje == 0:
            for preg in self.preguntas:
                self.puntaje += preg.get_muestra() * preg.get_puntaje()
        return self.puntaje

    def get_latex(self) -> str:
        """Genera el código LaTeX de la sección."""
        logging.debug('Entrando a Seccion.get_latex ...')
        # Diccionario de variables definidas por el usuario. Se define
        # en general para la sección, porque en caso de que el orden
        # de la sección **no** sea aleatorio, permite generar preguntas
        # en cascada.
        dParams: Dict[str, Any] = {}
        # Primero vamos a generar una lista de preguntas completas. Si
        # se requiere que sean aleatorias, se construyen, se reordenan,
        # se unen, y al final se agregan a la parte inicial de la
        # sección.
        templs: List[Latex] = []
        sublista: List[str] = []
        # Vamos agregando el texto de cada pregunta de la sección.
        filelist: List[str]
        texto: str
        preg: Pregunta
        for preg in self.preguntas:
            # Extraemos las preguntas.
            filelist = __muestra__(preg)
            # El puntaje de la pregunta es 0. Entonces debe corresponder
            # a un archivo de encabezado. Por eso no va entre
            # \begin{ejer} y \end{ejer}. Solo se puede extraer un
            # archivo y debemos estar en un bloque.
            if preg.get_puntaje() == 0:
                assert(preg.muestra == 1)
                assert(preg.es_bloque())
                texto = pregunta.get_latex(filelist[0], dParams)
                sublista.append('%s\n\\bigskip\n\n' % texto)
                continue

            sublista = __lista_latex__(preg, filelist, templs, sublista,
                                       dParams)

        # Si las preguntas se requieren en orden aleatorio, entonces
        # las reordenamos
        if self.aleatorias:
            logging.debug('Random: Reordenando las preguntas.')
            random.shuffle(templs)

        # Eliminando sublistas.
        lista: List[str]
        lista = __flatten_latex__(templs)

        # Concatenamos las instrucciones y colocamos al
        # final todas las preguntas.
        if len(self.instrucciones) == 0:
            return '%s\n\n' % ''.join(lista).strip()
        return '%s%s%s%s%s\n\n' % ('\\noindent\\rule{\\textwidth}{1pt}\n\n',
                                   self.instrucciones,
                                   '\n\n\\noindent\\rule{\\textwidth}{1pt}',
                                   '\n\n\\bigskip\n\n',
                                   ''.join(lista).strip())

    def get_respuestas(self) -> List[Respuesta]:
        """
        Genera una lista de instancias del objeto Respuesta,
        correspondiente a las preguntas de la sección.
        """
        logging.debug('Entrando a Seccion.get_respuestas ...')
        # Diccionario de variables definidas por el usuario. Se define
        # en general para la sección.
        dParams: Dict[str, Any] = {}
        # Se genera la lista de instancias del objeto Respuesta, y una
        # sublista en el caso de que haya un bloque. Si se requiere que
        # sean aleatorias, se reordenan (sin reordenar los bloques).
        lista: List[Resps] = []
        sublista: List[Respuesta] = []
        # Vamos agregando la instancia de cada respuesta de la sección.
        filelist: List[str]
        preg: Pregunta
        for preg in self.preguntas:
            # Extraemos las preguntas.
            filelist = __muestra__(preg)
            # Obtenemos la lista de respuestas.
            sublista = __lista_resps__(preg, filelist, lista, sublista,
                                       dParams)
        # Si las preguntas se requieren en orden aleatorio, entonces
        # se reordenan igual las respuestas.
        if self.aleatorias:
            logging.debug('Random: Reordenando las respuestas.')
            random.shuffle(lista)
        nueva: List[Respuesta] = __flatten_resps__(lista)

        # Nada más que hacer.
        return nueva

    def get_numPreguntas(self) -> int:
        """ Devuelve el número de preguntas de la sección. """
        resp: int = 0
        preg: Pregunta
        for preg in self.preguntas:
            if preg.get_puntaje() > 0:
                resp += preg.get_muestra()
        return resp


def __muestra__(preg: Pregunta) -> List[str]:
    """Escoje una muestra de preguntas de una dirección.

    La dirección dada puede ser una carpeta o una pregunta.  Si es
    un archivo (de tipo pregunta), simplemente devuelve el nombre
    del archivo. Si es una carpeta, entonces de la carpeta escoge de
    manera aleatoria el número de archivos indicados.

    La extensión del archivo de tipo pregunta está definida en
    Info.EXTENSION.
    """
    path: str = preg.origen
    resp: List[str]
    muestra = preg.get_muestra()
    # Es un archivo.
    if path.endswith(Info.EXTENSION):
        assert(muestra <= 1)
        return [path]
    # Debe ser una carpeta.
    if not path.endswith('/'):
        path = '%s/' % path
    # Generando la lista de archivos de tipo pregunta. Se asume que
    # la dirección es una carpeta.
    lista: List[str] = sorted(['%s%s' % (path, yo) for yo in os.listdir(path)
                               if yo.endswith(Info.EXTENSION)])
    logging.debug('Lista de archivos (se requieren %d):' % muestra)
    logging.debug('Path = %s' % path)
    logging.debug('%s' % str([yo.replace(path, '') for yo in lista]))
    if muestra < len(lista):
        # Devolviendo una muestra ordenada.
        logging.debug('Random: Muestra = %d' % muestra)
        resp = sorted(random.sample(lista, muestra))
    elif muestra == len(lista):
        resp = lista
    else:
        logging.critical(
                'La carpeta no tiene la cantidad de preguntas requeridas.')
        sys.exit()
    return resp


def __lista_latex__(preg: Pregunta, filelist: List[str], lista: List[Latex],
                    sublista: List[str], dParams: Dict[str, Any]) -> List[str]:
    filename: str
    texto: str
    fin: str
    for filename in filelist:
        texto = pregunta.get_latex(filename, dParams)
        # Estamos en un bloque y no es la última pregunta.
        if preg.bloque > 0:
            fin = '\\bigskip'
        else:
            fin = '\\newpage'
            dParams.clear()

        if preg.get_puntaje() > 1:
            txtPts = 'puntos'
        else:
            txtPts = 'punto'
        texto = '%s{[%d %s]}\n%s\n%s\n%s\n\n' % (
                '  \\begin{ejer}~\\textbf', preg.get_puntaje(), txtPts,
                texto, '\\end{ejer}', fin)
        if preg.es_bloque():
            sublista.append(texto)
        else:
            lista.append(texto)

        # Es la última pregunta del bloque. Agregamos la lista de
        # preguntas del bloque al bloque principal y reiniciamos
        if preg.es_ultima():
            lista.append(sublista)
            sublista = []
    return sublista


def __lista_resps__(preg: Pregunta, filelist: List[str], lista: List[Resps],
                    sublista: List[Respuesta],
                    dParams: Dict[str, Any]) -> List[Respuesta]:
    filename: str
    for filename in filelist:
        resp = pregunta.get_respuesta(filename, dParams)
        # Es un encabezado. Después de haber leído las variables podemos
        # continuar.
        if (resp.tipoPreg & TPreg.ENCABEZADO):
            continue
        resp.set_puntaje(preg.get_puntaje())
        if preg.es_bloque():
            sublista.append(resp)
        else:
            lista.append(resp)

    # Es la última pregunta del bloque. Agregamos la lista de
    # preguntas del bloque al bloque principal y reiniciamos
    if preg.es_ultima():
        lista.append(sublista)
        sublista = []

    # No estamos en un bloque o es la última pregunta.
    if preg.bloque <= 0:
        logging.debug('Borrando parámetros anteriores')
        dParams = {}

    return sublista


def __flatten_latex__(lista: List[Latex]) -> List[str]:
    nueva: List[str] = []
    elem: Latex
    cada: str
    for elem in lista:
        if isinstance(elem, list):
            for cada in elem:
                assert(isinstance(cada, str))
                nueva.append(cada)
        else:
            assert(isinstance(elem, str))
            nueva.append(elem)
    return nueva


def __flatten_resps__(lista: List[Resps]) -> List[Respuesta]:
    nueva: List[Respuesta] = []
    elem: Resps
    cada: Respuesta
    for elem in lista:
        if isinstance(elem, list):
            for cada in elem:
                assert(isinstance(cada, Respuesta))
                nueva.append(cada)
        else:
            assert(isinstance(elem, Respuesta))
            nueva.append(elem)
    return nueva
