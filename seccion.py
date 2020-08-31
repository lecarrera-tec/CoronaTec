import logging
import os
import random
from typing import List, Tuple

import Info
import pregunta
import parserPPP
from respuesta import Respuesta

# TODO Revisar errores mientras se leen los archivos, manejar 
# excepciones e informar al usario utilizando logging.

class Seccion:
    """Parseado de secci\'on de pruebas de preguntas parametrizadas.

    Guarda:
      - el t\'itulo de la secci\'on
      - instrucciones espec\'ificas (si las hubiera)
      - y lo importante, que es la direcci\'on (path) de cada una de las 
        preguntas. Puede ser una carpeta o un archivo tipo 
        Info.EXTENSION.
    """
    def __init__(self, f, dir_trabajo: str, aleatorio: bool = False):
        """Constructor a partir de archivo y el orden de las preguntas.

        Se supone que la \'ultima l\'inea que se ley\'o del archivo es 
        justamente la etiqueta para la secci\'on, y por eso estamos ac\'a.

        Aqu\'i se definen:
          - titulo: titulo de la secci\'on, si tiene.
          - instrucciones: si son dadas por el usuario.
          - puntaje: puntaje total de la secci\'on
          - preguntas: tuplas [int, str, int], formadas por el puntaje,
                       el origen y el tama\~no de la muestra de la 
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

        # Si tenemos un t\'itulo
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

        # Deber\'ian de seguir las direcciones a los archivos de las 
        # preguntas.
        assert(l.strip().startswith(Info.PREGUNTAS))
        # Vamos a guardar una lista de tuplas, donde el primer 
        # elemento es el puntaje, y el segundo la direcci\'on.
        self.preguntas: List[Tuple[int, str, int]] = []
        # Guardamos cada l\'inea, hasta que encontremos la primera 
        # l\'inea en blanco: esto se\~nala el final de la secci\'on.
        texto: str
        puntos: int
        muestra: int
        while True:
            l = f.readline().strip()
            # L\'inea en blanco, terminamos.
            if len(l) == 0:
                break
            # Si es un comentario, continuamos con la siguiente l\'inea.
            if l[0] == Info.COMMENT:
                continue
            # Buscamos los puntos de la pregunta, el tama\~no de la 
            # muestra y el origen de la pregunta.
            puntos = 1
            texto = parserPPP.derecha_igual(l, 'puntaje')
            if len(texto) > 0:
                try:
                    puntos = int(texto)
                except:
                    puntos = 1
                    texto = '%s "%s".\n%s' % (
                            'No se pudo leer puntaje en', l, 
                            'Por defecto queda en 1 pt')
                    logging.warning(texto)
            # Buscamos si define el tama\~no de la muestra.
            muestra = 1
            texto = parserPPP.derecha_igual(l, 'muestra')
            if len(texto) > 0:
                try:
                    muestra = int(texto)
                except:
                    muestra = 1
                    texto = '%s "%s".\n%s' % (
                            'No se pudo leer tama\~no de la muestra en', l, 
                            'Por defecto queda de tama\~no 1')
                    logging.warning(texto)
            # Ahora seguimos con el origen de la pregunta.
            texto = parserPPP.derecha_igual(l, 'origen')
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
        """Devuelve el puntaje total de la secci\'on."""
        if self.puntaje == 0:
            for preg in self.preguntas:
                self.puntaje += preg[0]
        return self.puntaje

    def get_latex(self) -> str:
        """Genera el c\'odigo LaTeX de la secci\'on."""
        logging.debug('Entrando a Seccion.get_latex ...')
        # Primero vamos a generar una lista de preguntas completas. Si 
        # se requiere que sean aleatorias, se construyen, se reordenan, 
        # se unen, y al final se agregan a la parte inicial de la 
        # secci\'on.
        lista: List[str] = []
        # Vamos agregando el texto de cada pregunta de la secci\'on.
        puntaje: int
        filelist: List[str]
        k: int   # Tama\~no de la muestra.
        texto: str
        for path in self.preguntas:
            puntaje = path[0]
            k = path[2]
            filelist = Seccion.muestraPreguntas(path[1], k)
            for filename in filelist:
                texto = '  \\begin{ejer}[%d %s]\n' % (
                        puntaje, 'pts' if puntaje > 1 else 'pt')
                lista.append('%s%s%s' % (
                    texto, 
                    pregunta.get_latex(filename),
                    #'\\end{ejer}\n\\bigskip\n\\pagebreak[3]\n'
                    '\\end{ejer}\n\\newpage\n\n'
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
                ' pts\n\\nopagebreak\n'
        )
        # Concatenamos las instrucciones, el puntaje y colocamos al 
        # final todas las preguntas.
        return '%s%s%s\n\n' % (self.instrucciones, texto, 
                               ''.join(lista).strip())

    def get_respuestas(self) -> List[Respuesta]:
        """
        Genera una lista de intancias del objeto Respuesta, 
        correspondiente a las preguntas de la secci\'on.
        """
        logging.debug('Entrando a Seccion.get_respuestas ...')
        # Se genera la lista de instancias del objeto Respuesta. Si se 
        # requiere que sean aleatorias, se reordenan.
        lresp: List[Respuesta] = []
        # Vamos agregando la instancia de cada pregunta de la secci\'on.
        puntaje: int
        filelist: List[str]
        k: int   # Tama\~no de la muestra.
        for path in self.preguntas:
            puntaje = path[0]
            k = path[2]
            filelist = Seccion.muestraPreguntas(path[1], k)
            for filename in filelist:
                resp = pregunta.get_respuesta(filename)
                resp.set_puntaje(puntaje)
                lresp.append(resp)

        # Si las preguntas se requieren en orden aleatorio, entonces
        # se reordenan igual las respuestas.
        if self.aleatorias: 
            logging.debug('Reordenando las respuestas.')
            random.shuffle(lresp)

        # Nada m\'as que hacer.
        return lresp

    def get_numPreguntas(self) -> int:
        """ Devuelve el n\'umero de preguntas de la secci\'on. """
        resp: int = 0
        for cada in self.preguntas:
            resp += cada[2]
        return resp

    @staticmethod
    def muestraPreguntas(path: str, muestra: int) -> List[str]:
        """Escoje una muestra de preguntas de una direcci\'on.

        La direcci\'on dada puede ser una carpeta o una pregunta.  Si es 
        un archivo (de tipo pregunta), simplemente devuelve el nombre 
        del archivo. Si es una carpeta, entonces de la carpeta escoge de 
        manera aleatoria el n\'umero de archivos indicados.

        La extensi\'on del archivo de tipo pregunta est\'a definida en 
        Info.EXTENSION.
        """
        # Es un archivo.
        if path.endswith(Info.EXTENSION):
            if (muestra > 1):
                logging.error('No es una carpeta. S\'olo se agrega una pregunta.')
            return [path]

        # Debe ser una carpeta.
        if not path.endswith('/'):
            path = '%s/' % path
        # Generando la lista de archivos de tipo pregunta. Se asume que
        # la direcci\'on es una carpeta.
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
            # El tama\~no de la muestra es el tama\~no de la lista.
            return lista
