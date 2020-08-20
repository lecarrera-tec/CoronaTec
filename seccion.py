from typing import List, Tuple
import os
import random

import info
import pregunta

class Seccion:
    """Parseado de sección de pruebas de preguntas parametrizadas.

    Guarda:
      - el título de la sección
      - instrucciones específicas (si las hubiera)
      - y lo importante, que es la dirección (path) de cada una de las 
        preguntas. Puede ser una carpeta o un archivo tipo '.preg'
    """
    def __init__(self, f, rand: bool = False):
        """Constructor a partir de archivo y el orden de las preguntas.

        Se supone que la última línea que se leyó del archivo es 
        justamente la etiqueta para la sección, y por eso estamos acá.

        Aquí se definen:
            - titulo: titulo de la sección, si tiene.
            - instrucciones: si son dadas por el usuario.
            - puntaje: puntaje total de la sección
            - paths: tuplas [int, str], formadas por el puntaje de la 
                     pregunta y la dirección
            - aleatorias: Si el orden de las preguntas debe ser
                          aleatorio o no.
        """
        self.puntaje: int = 0
        self.aleatorias: bool = rand

        # Nos brincamos los comentarios y los espacios en blanco.
        ignorar: bool = True
        while ignorar:
            l: str = f.readline().strip()
            ignorar = len(l) == 0 or l[0] == info.COMMENT

        # Si tenemos un título
        if l == info.TITULO:
            self.titulo: str = f.readline().strip()
            print('<Titulo>: %s' % self.titulo)
            # y nos brincamos los comentarios y espacios en blanco
            ignorar = True
            while ignorar:
                l = f.readline().strip()
                ignorar = len(l) == 0 or l[0] == info.COMMENT
        else:
            self.titulo = ''

        # Tenemos instrucciones.
        if l == info.INSTRUCCIONES:
            l = f.readline()
            self.instrucciones: List[str] = []
            while l.find(info.ABRIR) == -1:
                self.instrucciones.append(l)
                l = f.readline()

        # Deberían de seguir las direcciones a los archivos de las 
        # preguntas.
        print('??: %s' % l)
        assert(l.strip().startswith(info.PREGUNTAS))
        # Vamos a guardar una lista de tuplas, donde el primer 
        # elemento es el puntaje, y el segundo la dirección.
        self.paths: List[Tuple[int, str]] = []
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
                if idx > 0:  # <pts>,<path>
                    self.paths.append((int(l[0:idx]), l[idx+1:].strip()))
                else:  # <path>, entonces por default el puntaje es 1.
                    self.paths.append((1, l[idx+1:].strip()))

    def get_puntaje(self) -> int:
        """Devuelve el puntaje total de la sección."""
        if self.puntaje > 0:
            for preg in self.paths:
                self.puntaje += preg[0]
        return self.puntaje

    def get_latex(self) -> List[str]:
        """Genera el código LaTeX de la sección."""
        # Comenzamos por las instrucciones de la sección.
        tex: List[str] = self.instrucciones
        # Agregamos el puntaje.
        tex.append('\\noindent\\textbf{Puntaje:} %d pts' 
                          % self.get_puntaje())
        tex.append('')
        # Si las preguntas se presentan en orden aleatorio, entonces
        # las revolvemos
        if self.aleatorias: 
            random.shuffle(self.paths)
        # Vamos agregando el texto de cada pregunta de la sección.
        for path in self.paths:
            puntaje: int = path[0]
            filename: str = Seccion.choose_question(path[1])

            tex.append('\\begin{ejer}[%d %s]' 
                              % (puntaje, 'pts' if puntaje > 1 else 'pt'))
            tex += pregunta.get_latex(filename)
            tex.append('\\end{ejer}')
        return tex

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

        # Generando la lista de archivos de tipo pregunta. Se asume que
        # el path es una carpeta.
        lista: List[str] = []
        for me in os.listdir(path):
            if me.endswith(info.EXTENSION):
                lista.append(me)

        # Se devuelve un elemento al azar.
        return random.choice(lista)
