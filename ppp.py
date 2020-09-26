import logging
import sys
from typing import List

import Info
import leer
from seccion import Seccion


class PPP:
    """ Clase principal para las Pruebas de Preguntas Parametrizadas

    Variables
    ---------
    cursos:
        Nombre de los cursos.
    dirTrabajo:
        Dirección a la carpeta de la prueba. Se requiere porque la
        dirección de las preguntas es relativa a dicha carpeta.
    encabezado:
        Encabezado a agregar a LaTeX
    escuelas:
        Lista de escuelas del examen.
    instrucciones:
        Instrucciones de la prueba.
    puntaje
        Puntaje total de la prueba.
    secciones:
        Una lista de instancias de la clase seccion
    semestre:
        Texto del semestre y año.
    tiempo:
        Duración de la prueba.
    titulo:
        Título de la prueba.
    """

    def __init__(self, filename: str):
        """ Constructor.

        Argumentos
        ----------
        filename:
            La direccion un archivo de tipo .ppp
        """
        # Definimos el puntaje total como 0, de manera temporal.
        self.puntaje = 0

        # Definimos el directorio local como el directorio de trabajo,
        # pero si la dirección dada no es un archivo en el directorio
        # actual, entonces vamos a guardar la dirección al archivo,
        # porque la referencia a los archivos de las preguntas es
        # relativa al directorio del archivo principal.
        self.dirTrabajo: str = './'
        idx = filename.rfind('/')
        if idx > 0:
            self.dirTrabajo = filename[0:idx+1]

        # Vamos a leer el archivo linea x linea. Por lo general se van
        # a ignorar lineas en blanco y lineas que comiencen con el
        # caracter de comentario.
        try:
            finp = open(filename, 'r')
        except OSError:
            logging.critical('No se pudo abrir archivo principal.')
            sys.exit()
        lsTexto: List[str] = finp.readlines()
        finp.close()

        linea: str = leer.blancos(lsTexto)
        hayEtiqueta: bool

        # Lo primero que deberíamos encontrar en el archivo es el nombre
        # de las escuelas. Obligatorio.
        self.escuelas: List[str]
        self.escuelas, linea = leer.escuelas(linea, lsTexto)
        logging.info('<Escuelas>: %s' % ', '.join(self.escuelas))

        # Sigue el texto del semestre. Obligatorio.
        self.semestre: str
        self.semestre, linea = leer.semestre(linea, lsTexto)
        logging.info('<Semestre>: %s' % self.semestre)

        # Guardamos el texto del tiempo. Obligatorio.
        self.tiempo: str
        self.tiempo, linea = leer.tiempo(linea, lsTexto)
        logging.info('%s: %s' % (Info.TIEMPO, self.tiempo))

        # Ahora sigue el nombre de los cursos. Obligatorio.
        self.cursos: List[str]
        self.cursos, linea = leer.cursos(linea, lsTexto)
        logging.info('<Cursos>: %s' % ', '.join(self.cursos))

        # Sigue el título de la prueba. Obligatorio.
        self.titulo, linea = leer.titulo(linea, lsTexto)
        logging.info('<Titulo>: %s' % self.titulo)

        # Ahora revisamos si existe encabezado para LaTeX. Si no
        # hubiera encabezado, se tiene un texto vac\'io.
        self.encabezado, linea = leer.encabezado(linea, lsTexto)
        if len(self.encabezado) > 0:
            logging.info('<Encabezado>')
            logging.info(self.encabezado)
        else:
            logging.info('No se encontró encabezado.')

        # Revisamos si siguen las instrucciones. Pueden abarcar varias
        # líneas de texto. Si no hubiera instrucciones, observe que
        # entonces la variable sería un texto vacío.
        self.instrucciones, linea = leer.instrucciones(linea, lsTexto)
        if len(self.instrucciones) > 0:
            logging.info('<Instrucciones>')
            logging.info(self.instrucciones)
        else:
            logging.info('No se encontraron instrucciones.')

        # No queda de otra. Tienen que seguir las secciones. Una lista
        # de instancias de la clase Seccion.
        assert(linea.startswith(Info.LSECCION))
        self.secciones: List[Seccion]
        self.secciones = leer.secciones(linea, lsTexto, self.dirTrabajo)

        # ¡¡¡Terminamos!!!
        logging.info('Fin de PPP\n')

    def get_puntaje(self) -> int:
        """
        Calcula el puntaje total de la prueba.
        """
        if self.puntaje == 0:
            for cada in self.secciones:
                self.puntaje += cada.get_puntaje()
        return self.puntaje

    # TODO No contar las preguntas de tipo encabezado.
    def get_numPreguntas(self) -> List[int]:
        """
        Devuelve el número de preguntas por cada una de las secciones.
        """
        lista: List[int] = []
        for cada in self.secciones:
            lista.append(cada.get_numPreguntas())
        return lista
