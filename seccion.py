import logging
import os
import random
from typing import Any, Dict, List, Tuple

import Info
import pregunta
import parserPPP
from respuesta import Respuesta

# TODO Revisar errores mientras se leen los archivos, manejar 
# excepciones e informar al usario utilizando logging.

class Seccion:
    """Parseado de sección de pruebas de preguntas parametrizadas.

    Atributos
    ---------
    aleatorias : bool
        Si las preguntas se quieren (o no) en orden aleatorio. El
        predeterminado es que no.
    instrucciones : str
        Texto de las instrucciones específicas de la sección.
    preguntas : [(int, str, int)]
        Una lista de tuplas. La información de la tupla corresponde
        al puntaje de la pregunta, el path, y el número de muestras
        que se extrae en caso de que sea una carpeta.
    puntaje : int
        Puntaje total de la sección.
    titulo : str
        El título de la sección.
    """
    def __init__(self, f, dir_trabajo: str, aleatorio: bool = False):
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

        # Nos brincamos los comentarios y los espacios en blanco.
        ignorar: bool = True
        l : str
        while ignorar:
            l = f.readline().strip()
            ignorar = len(l) == 0 or l[0] == Info.COMMENT

        # Si tenemos un título
        if l == Info.TITULO:
            self.titulo: str = f.readline().strip()
            logging.info('<Titulo>: %s' % self.titulo)
            # y nos brincamos los comentarios y espacios en blanco
            ignorar = True
            while ignorar:
                l = f.readline().strip()
                ignorar = len(l) == 0 or l[0] == Info.COMMENT
        else:
            self.titulo = ''

        # Tenemos instrucciones.
        lista: List[str] = []
        if l == Info.INSTRUCCIONES:
            l = f.readline()
            while l.find(Info.ABRIR) == -1:
                lista.append(l)
                l = f.readline()
            self.instrucciones = '%s\n' % ''.join(lista)
        else:
            self.instrucciones = ''

        # Deberían de seguir las direcciones a los archivos de las 
        # preguntas.
        assert(l.strip().startswith(Info.PREGUNTAS))
        # Vamos a guardar una lista de tuplas, donde el primer 
        # elemento es el puntaje, y el segundo la dirección.
        self.preguntas: List[Tuple[int, str, int]] = []
        # Guardamos cada línea, hasta que encontremos la primera 
        # línea en blanco: esto señala el final de la sección.
        texto: str
        puntos: int
        muestra: int
        while True:
            l = f.readline().strip()
            # Línea en blanco, terminamos.
            if len(l) == 0:
                break
            # Si es un comentario, continuamos con la siguiente línea.
            if l[0] == Info.COMMENT:
                continue
            # Buscamos los puntos de la pregunta, el tamaño de la 
            # muestra y el origen de la pregunta.
            puntos = 1
            texto = parserPPP.derechaIgual(l, 'puntaje')
            if len(texto) > 0:
                try:
                    puntos = int(texto)
                except:
                    puntos = 1
                    texto = '%s "%s".\n%s' % (
                            'No se pudo leer puntaje en', l, 
                            'Por defecto queda en 1 pt')
                    logging.warning(texto)
            # Buscamos si define el tamaño de la muestra.
            muestra = 1
            texto = parserPPP.derechaIgual(l, 'muestra')
            if len(texto) > 0:
                try:
                    muestra = int(texto)
                except:
                    muestra = 1
                    texto = '%s "%s".\n%s' % (
                            'No se pudo leer tamaño de la muestra en', l, 
                            'Por defecto queda de tamaño 1')
                    logging.warning(texto)
            # Ahora seguimos con el origen de la pregunta.
            texto = parserPPP.derechaIgual(l, 'origen')
            if len(texto) == 0:
                texto = '%s "%s".\n%s' % (
                        'No se pudo leer origen de pregunta en', l, 
                        'La pregunta no se pudo incluir.')
                logging.error(texto)
                continue
            self.preguntas.append(
                    (puntos, '%s%s' % (dir_trabajo, texto), muestra))
            logging.info('Se agrega pregunta: %s' % str(self.preguntas[-1]))

    def get_puntaje(self) -> int:
        """Devuelve el puntaje total de la sección."""
        if self.puntaje == 0:
            for preg in self.preguntas:
                self.puntaje += preg[0]
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
        lista: List[str] = []
        # Vamos agregando el texto de cada pregunta de la sección.
        puntaje: int
        filelist: List[str]
        k: int   # Tamaño de la muestra.
        texto: str
        for path in self.preguntas:
            # Si el orden es aleatorio, se borran las variables ya
            # definidas.
            if self.aleatorias:
                dParams = {}
            puntaje = path[0]
            k = path[2]
            filelist = Seccion.muestraPreguntas(path[1], k)
            for filename in filelist:
                texto = '  \\begin{ejer}~\\textbf{[%d %s]}\n' % (
                        puntaje, 'puntos' if puntaje > 1 else 'punto')
                lista.append('%s%s%s' % (
                    texto, 
                    pregunta.get_latex(filename, dParams),
                    #'\\end{ejer}\n\\bigskip\n\\pagebreak[3]\n'
                    '\\end{ejer}\n\\newpage\n\n'
                ))

        # Si las preguntas se requieren en orden aleatorio, entonces
        # las reordenamos
        if self.aleatorias: 
            logging.debug('Reordenando las preguntas.')
            random.shuffle(lista)

        # Concatenamos las instrucciones y colocamos al 
        # final todas las preguntas.
        return '%s%s\n\n' % (self.instrucciones, ''.join(lista).strip())

    def get_respuestas(self) -> List[Respuesta]:
        """
        Genera una lista de intancias del objeto Respuesta, 
        correspondiente a las preguntas de la sección.
        """
        logging.debug('Entrando a Seccion.get_respuestas ...')
        # Diccionario de variables definidas por el usuario. Se define
        # en general para la sección, porque en caso de que el orden
        # de la sección **no** sea aleatorio, permite generar preguntas
        # en cascada.
        dParams: Dict[str, Any] = {}
        # Se genera la lista de instancias del objeto Respuesta. Si se 
        # requiere que sean aleatorias, se reordenan.
        lresp: List[Respuesta] = []
        # Vamos agregando la instancia de cada pregunta de la sección.
        puntaje: int
        filelist: List[str]
        k: int   # Tamaño de la muestra.
        for path in self.preguntas:
            # Si el orden es aleatorio, se borran las variables ya
            # definidas.
            if self.aleatorias:
                dParams = {}
            puntaje = path[0]
            k = path[2]
            filelist = Seccion.muestraPreguntas(path[1], k)
            for filename in filelist:
                resp = pregunta.get_respuesta(filename, dParams)
                resp.set_puntaje(puntaje)
                lresp.append(resp)

        # Si las preguntas se requieren en orden aleatorio, entonces
        # se reordenan igual las respuestas.
        if self.aleatorias: 
            logging.debug('Reordenando las respuestas.')
            random.shuffle(lresp)

        # Nada más que hacer.
        return lresp

    def get_numPreguntas(self) -> int:
        """ Devuelve el número de preguntas de la sección. """
        resp: int = 0
        for cada in self.preguntas:
            resp += cada[2]
        return resp

    @staticmethod
    def muestraPreguntas(path: str, muestra: int) -> List[str]:
        """Escoje una muestra de preguntas de una dirección.

        La dirección dada puede ser una carpeta o una pregunta.  Si es 
        un archivo (de tipo pregunta), simplemente devuelve el nombre 
        del archivo. Si es una carpeta, entonces de la carpeta escoge de 
        manera aleatoria el número de archivos indicados.

        La extensión del archivo de tipo pregunta está definida en 
        Info.EXTENSION.
        """
        # Es un archivo.
        if path.endswith(Info.EXTENSION):
            if (muestra > 1):
                logging.error('No es una carpeta. Sólo se agrega una pregunta.')
            return [path]

        # Debe ser una carpeta.
        if not path.endswith('/'):
            path = '%s/' % path
        # Generando la lista de archivos de tipo pregunta. Se asume que
        # la dirección es una carpeta.
        lista: List[str] = []
        for me in os.listdir(path):
            if me.endswith(Info.EXTENSION):
                lista.append('%s%s' % (path, me))

        if muestra > len(lista):
            logging.error('La carpeta no tiene la cantidad de preguntas requeridas')
            return lista
        elif muestra < len(lista):
            # Devolviendo una muestra ordenada.
            idx: List[int] = random.sample([*range(len(lista))], muestra)
            idx.sort()
            return [lista[i] for i in idx]
        else:
            # El tamaño de la muestra es el tamaño de la lista.
            return lista
