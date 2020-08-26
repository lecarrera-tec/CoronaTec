import logging
import os
import random
from typing import List, Tuple

import info
import pregunta
import parser

# TODO Revisar errores mientras se leen los archivos, manejar 
# excepciones e informar al usario utilizando logging.

class Seccion:
    """Parseado de sección de pruebas de preguntas parametrizadas.

    Guarda:
      - el título de la sección
      - instrucciones específicas (si las hubiera)
      - y lo importante, que es la dirección (path) de cada una de las 
        preguntas. Puede ser una carpeta o un archivo tipo 
        info.EXTENSION.
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
            ignorar = len(l) == 0 or l[0] == info.COMMENT

        # Si tenemos un título
        if l == info.TITULO:
            self.titulo: str = f.readline().strip()
            logging.info('<Titulo>: %s' % self.titulo)
            # y nos brincamos los comentarios y espacios en blanco
            ignorar = True
            while ignorar:
                l = f.readline().strip()
                ignorar = len(l) == 0 or l[0] == info.COMMENT
        else:
            self.titulo = ''

        # Tenemos instrucciones.
        lista: List[str] = []
        if l == info.INSTRUCCIONES:
            l = f.readline()
            while l.find(info.ABRIR) == -1:
                lista.append(l)
                l = f.readline()
            self.instrucciones = '%s\n' % ''.join(lista)

        # Deberían de seguir las direcciones a los archivos de las 
        # preguntas.
        assert(l.strip().startswith(info.PREGUNTAS))
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
            if l[0] == info.COMMENT:
                continue
            # Buscamos los puntos de la pregunta, el tamaño de la 
            # muestra y el origen de la pregunta.
            puntos = 1
            texto = parser.derecha_igual(l, 'puntaje')
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
            texto = parser.derecha_igual(l, 'muestra')
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
            texto = parser.derecha_igual(l, 'origen')
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
            puntaje = path[0]
            k = path[2]
            filelist = Seccion.muestra_preguntas(path[1], k)
            for filename in filelist:
                texto = '  \\begin{ejer}[%d %s]\n' % (
                        puntaje, 'pts' if puntaje > 1 else 'pt')
                lista.append('%s%s%s' % (
                    texto, 
                    pregunta.get_latex(filename),
                    '\\end{ejer}\n\\bigskip\n\\pagebreak[2]\n'
                ))

        # Si las preguntas se requieren en orden aleatorio, entonces
        # las reordenamos
        if self.aleatorias: 
            logging.debug('Reordenando las preguntas.')
            random.shuffle(lista)

        # Construimos el texto del puntaje total.
        texto = '%s%d%s' % (
                '  \\noindent\\textbf{Puntaje:} ', 
                self.get_puntaje(),
                'pts\n\\nopagebreak\n'
        )
        # Concatenamos las instrucciones, el puntaje y colocamos al 
        # final todas las preguntas.
        return '%s%s%s\n\n' % (self.instrucciones, texto, 
                               ''.join(lista).strip())

    def get_respuestas(self):
        """
        Genera una lista de intancias del objeto Respuesta, 
        correspondiente a las preguntas de la sección.
        """
        logging.debug('Entrando a Seccion.get_respuestas ...')
        # Se genera la lista de instancias del objeto Respuesta. Si se 
        # requiere que sean aleatorias, se reordenan.
        lresp = []
        # Vamos agregando la instancia de cada pregunta de la sección.
        puntaje: int
        filelist: List[str]
        k: int   # Tamaño de la muestra.
        for path in self.preguntas:
            puntaje = path[0]
            k = path[2]
            filelist = Seccion.muestra_preguntas(path[1], k)
            for filename in filelist:
                resp = pregunta.get_respuesta(filename)
                resp.set_puntaje(puntaje)
                lresp.append(resp)

        # Si las preguntas se requieren en orden aleatorio, entonces
        # se reordenan igual las respuestas.
        if self.aleatorias: 
            logging.debug('Reordenando las respuestas.')
            random.shuffle(lresp)

        # Nada más que hacer.
        return lresp

    @staticmethod
    def muestra_preguntas(path: str, muestra: int) -> List[str]:
        """Escoje una muestra de preguntas de una dirección.

        La dirección dada puede ser una carpeta o una pregunta.  Si es 
        un archivo (de tipo pregunta), simplemente devuelve el nombre 
        del archivo. Si es una carpeta, entonces de la carpeta escoge de 
        manera aleatoria el número de archivos indicados.

        La extensión del archivo de tipo pregunta está definida en 
        info.EXTENSION.
        """
        # Es un archivo.
        if path.endswith(info.EXTENSION):
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
            if me.endswith(info.EXTENSION):
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
