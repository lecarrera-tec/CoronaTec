from typing import List
import logging
import sys

from seccion import Seccion
import info
import parser
import latex

class PPP:
    """
    Clase principal para las Pruebas de Preguntas Parametrizadas

    Contiene la estructura principal:
      - El nombre del curso.
      - El título de la prueba.
      - Instrucciones generales para la prueba.
      - La lista de las secciones, que son a su vez una clase.
        (aquí es donde está la información importante)
    """

    def __init__(self, filename: str):
        """
        Constructor. Recibe como argumento la direccion un archivo 
        de tipo .ppp

        Devuelve la estructura principal, y la estructura anidada
        de cada una de las secciones.

        Se definen las variables:
            - dir_trabajo   : dirección a la carpeta de la prueba.
                              Se requiere porque la dirección de las
                              preguntas es relativa a dicha carpeta.
            - curso         : Nombre del curso.
            - titulo        : Título de la prueba.
            - instrucciones : Instrucciones de la prueba.
            - encabezado    : Encabezado a agregar a \LaTeX
            - secciones     : Una lista de instancias de la clase 
                              seccion
        """
        # Definimos el puntaje total como 0, de manera temporal.
        self.puntaje = 0

        # Definimos el directorio local como el directorio de trabajo, 
        # pero si la dirección dada no es un archivo en el directorio 
        # actual, entonces vamos a guardar la dirección al archivo, 
        # porque la referencia a los archivos de las preguntas es 
        # relativa al directorio del archivo principal. 
        # TODO Hay que pensar en una solución para las imágenes
        # en LaTeX.
        # Warning! Estamos pensando en linux!
        self.dir_trabajo: str = './'
        idx = filename.rfind('/')
        if idx > 0:
            self.dir_trabajo = filename[0:idx+1]

        # Vamos a leer el archivo linea x linea. Por lo general se van 
        # a ignorar lineas en blanco y lineas que comiencen con el 
        # caracter de comentario.
        try:
            finp = open(filename, 'r')
        except:
            logging.critical('No se pudo abrir archivo principal.')
            sys.exit()

        # Lo primero que deberíamos encontrar en el archivo es el nombre 
        # del curso. Buscamos primero la etiqueta.
        ignorar: bool = True
        while ignorar:
            l = finp.readline().strip()
            ignorar = len(l) == 0 or l[0] == info.COMMENT 
        assert(l == info.CURSO)

        # Guardamos el texto del nombre del curso.
        self.curso = finp.readline().strip()
        logging.info('<Curso>: %s' % self.curso)

        # Luego debería seguir el título de la prueba. Buscamos la 
        # etiqueta respectiva.
        ignorar = True
        while ignorar:
            l = finp.readline().strip()
            ignorar = len(l) == 0 or l[0] == info.COMMENT 
        assert(l == info.TITULO)

        # Guardamos el texto del titulo.
        self.titulo = finp.readline().strip()
        logging.info('<Titulo>: %s' % self.titulo)

        # Buscamos la siguiente etiqueta.
        ignorar = True
        while ignorar:
            l = finp.readline().strip()
            ignorar = len(l) == 0 or l[0] == info.COMMENT
        
        # Ahora revisamos si existe encabezado para LaTeX. Si no 
        # hubiera encabezado, observe que entonces la variable 
        # estaría en blanco.
        lista: List[str] = []
        continuar : bool
        if l == info.ENCABEZADO:
            l = finp.readline()
            while l.find(info.ABRIR) == -1:
                lista.append(l)
                l = finp.readline()
            logging.info('<Encabezado>')
            self.encabezado = '%s\n' % ''.join(lista).strip()
            logging.info(self.encabezado)
        else:
            self.encabezado = ''

        # Revisamos si son las instrucciones. Pueden abarcar varias 
        # líneas de texto. Si no hubiera instrucciones, observe que
        # entonces la variable estaría en blanco.
        lista = []
        if l.strip() == info.INSTRUCCIONES:
            l = finp.readline()
            while l.find(info.ABRIR) == -1:
                lista.append(l)
                l = finp.readline()
            logging.info('<Instrucciones>')
            self.instrucciones = '%s\n' % ''.join(lista).strip()
            logging.info(self.instrucciones)
        else:
            self.instrucciones = ''

        # No queda de otra. Tienen que seguir las secciones. Una lista 
        # de instancias de la clase Seccion.
        l = l.strip()
        assert(l.startswith(info.LSECCION))
        counter = 0
        self.secciones = [];
        es_aleatorio: bool = False
        while l.startswith(info.LSECCION):
            l = l.strip(info.STRIP)
            counter += 1
            logging.info('%d : Llamando a seccion ...' % counter)
            es_aleatorio = parser.derecha_igual(l, 'orden') == 'aleatorio'
            self.secciones.append(
                    Seccion(finp, self.dir_trabajo, es_aleatorio))
            l = finp.readline().strip()
        logging.info('Fin de PPP\n')

    def get_puntaje(self) -> int:
        """
        Calcula el puntaje total de la prueba.
        """
        if self.puntaje == 0:
            for cada in self.secciones:
                self.puntaje += cada.get_puntaje()
        return self.puntaje
