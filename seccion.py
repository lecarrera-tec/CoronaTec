import logging
import os
import random
from typing import List, Tuple

import info
import pregunta

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
            - preguntas: tuplas [int, str], formadas por el puntaje de 
                         la pregunta y la dirección
            - aleatorias: Si el orden de las preguntas debe ser
                          aleatorio o no.
        """
        self.puntaje: int = 0
        self.aleatorias: bool = aleatorio

        # Nos brincamos los comentarios y los espacios en blanco.
        ignorar: bool = True
        while ignorar:
            l: str = f.readline().strip()
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
        self.preguntas: List[Tuple[int, str]] = []
        # Guardamos cada línea, hasta que encontremos la primera 
        # línea en blanco: esto señala el final de la sección.
        while True:
            l = f.readline().strip()
            # Línea en blanco, terminamos.
            if len(l) == 0:
                break
            # Si no es un comentario, buscamos primero los puntos de 
            # la pregunta. Se guarda la tupla.
            elif l[0] != info.COMMENT:
                idx: int = l.find(',')
                pts: int = 1
                path: str = dir_trabajo + l[idx+1:].strip()
                if idx > 0:  # <pts>,<path>
                    pts = int(l[0:idx])
                self.preguntas.append((pts, path))
                logging.info(str(self.preguntas[-1]))

    def get_puntaje(self) -> int:
        """Devuelve el puntaje total de la sección."""
        if self.puntaje == 0:
            for preg in self.preguntas:
                self.puntaje += preg[0]
        return self.puntaje

    def get_latex(self) -> str:
        """Genera el código LaTeX de la sección."""
        logging.info('Entrando a Seccion.get_latex ...')
        lista: List[str] = []
        # Comenzamos por las instrucciones de la sección.
        lista.append(self.instrucciones)
        # Agregamos el puntaje.
        lista.append('  \\noindent\\textbf{Puntaje:} %d pts\n\n' 
                          % self.get_puntaje())
        # Si las preguntas se presentan en orden aleatorio, entonces
        # las revolvemos
        if self.aleatorias: 
            logging.info('Revolviendo las preguntas.')
            random.shuffle(self.preguntas)
        # Vamos agregando el texto de cada pregunta de la sección.
        puntaje: int
        filename: str
        for path in self.preguntas:
            puntaje = path[0]
            filename = Seccion.choose_question(path[1])
            lista.append('  \\begin{ejer}[%d %s]\n' 
                              % (puntaje, 'pts' if puntaje > 1 else 'pt'))
            lista.append(pregunta.get_latex(filename))
            lista.append('  \\end{ejer}\n\n')
        return ('%s\n' % ''.join(lista).strip())

    @staticmethod
    def choose_question(path: str) -> str:
        """Escoje una pregunta de una dirección.

        La dirección dada puede ser una carpeta o una pregunta.  Si es 
        un archivo (de tipo pregunta), simplemente devuelve el nombre 
        del archivo. Si es una carpeta, entonces de la carpeta escoge de 
        manera aleatoria un archivo de tipo pregunta.

        La extensión del archivo de tipo pregunta está definida en 
        info.EXTENSION.
        """
        if path.endswith(info.EXTENSION):
            return path

        if not path.endswith('/'):
            path = '%s/' % path
        # Generando la lista de archivos de tipo pregunta. Se asume que
        # la dirección es una carpeta.
        lista: List[str] = []
        for me in os.listdir(path):
            if me.endswith(info.EXTENSION):
                lista.append('%s%s' % (path, me))

        # Se devuelve un elemento al azar.
        return random.choice(lista)
