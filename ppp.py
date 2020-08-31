from typing import List
import logging
import sys

from seccion import Seccion
import Info
import parserPPP
import latex

class PPP:
    """
    Clase principal para las Pruebas de Preguntas Parametrizadas

    Contiene la estructura principal:
      - El nombre del curso.
      - El t\'itulo de la prueba.
      - Instrucciones generales para la prueba.
      - La lista de las secciones, que son a su vez una clase.
        (aqu\'i es donde est\'a la informaci\'on importante)
    """

    def __init__(self, filename: str):
        """
        Constructor. Recibe como argumento la direccion un archivo 
        de tipo .ppp

        Devuelve la estructura principal, y la estructura anidada
        de cada una de las secciones.

        Se definen las variables:
            - dir_trabajo   : direcci\'on a la carpeta de la prueba.
                              Se requiere porque la direcci\'on de las
                              preguntas es relativa a dicha carpeta.
            - escuelas      : Lista de escuelas del examen.
            - semestre      : Texto del semestre y a\~no.
            - tiempo        : Duraci\'on de la prueba.
            - cursos        : Nombre de los cursos.
            - titulo        : T\'itulo de la prueba.a
            - instrucciones : Instrucciones de la prueba.
            - encabezado    : Encabezado a agregar a \LaTeX
            - secciones     : Una lista de instancias de la clase 
                              seccion
        """
        # Definimos el puntaje total como 0, de manera temporal.
        self.puntaje = 0

        # Definimos el directorio local como el directorio de trabajo, 
        # pero si la direcci\'on dada no es un archivo en el directorio 
        # actual, entonces vamos a guardar la direcci\'on al archivo, 
        # porque la referencia a los archivos de las preguntas es 
        # relativa al directorio del archivo principal. 
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

        # Lo primero que deber\'iamos encontrar en el archivo es el nombre 
        # de las escuelas. Buscamos primero la etiqueta.
        ignorar: bool = True
        while ignorar:
            l = finp.readline().strip()
            ignorar = len(l) == 0 or l[0] == Info.COMMENT 
        assert(l == Info.ESCUELAS)
        # Agregamos todas las l\'ineas que no comiencen con comentario
        # hasta llegar a una l\'inea en blanco.
        self.escuelas: List[str] = []
        while True:
            l = finp.readline().strip()
            if len(l) == 0:
                break
            if l.startswith(Info.COMMENT):
                continue
            self.escuelas.append(l)
        logging.info('<Escuelas>: %s' % ', '.join(self.escuelas))

        # Sigue el semestre.
        ignorar = True
        while ignorar:
            l = finp.readline().strip()
            ignorar = len(l) == 0 or l[0] == Info.COMMENT 
        assert(l == Info.SEMESTRE)

        # Guardamos el texto del semestre.
        self.semestre = finp.readline().strip()
        logging.info('<Semestre>: %s' % self.semestre)

        # Sigue el tiempo.
        ignorar = True
        while ignorar:
            l = finp.readline().strip()
            ignorar = len(l) == 0 or l[0] == Info.COMMENT 
        assert(l == Info.TIEMPO)

        # Guardamos el texto del tiempo.
        self.tiempo = finp.readline().strip()
        logging.info('%s: %s' % (Info.TIEMPO, self.semestre))

        # Ahora sigue el nombre de los cursos. Buscamos primero la 
        # etiqueta.
        ignorar = True
        while ignorar:
            l = finp.readline().strip()
            ignorar = len(l) == 0 or l[0] == Info.COMMENT 
        assert(l == Info.CURSOS)
        # Agregamos todas las l\'ineas que no comiencen con comentario
        # hasta llegar a una l\'inea en blanco.
        self.cursos: List[str] = []
        while True:
            l = finp.readline().strip()
            if len(l) == 0:
                break
            if l.startswith(Info.COMMENT):
                continue
            self.cursos.append(l)
        logging.info('<Cursos>: %s' % ', '.join(self.cursos))

        # Luego deber\'ia seguir el t\'itulo de la prueba. Buscamos la 
        # etiqueta respectiva.
        ignorar = True
        while ignorar:
            l = finp.readline().strip()
            ignorar = len(l) == 0 or l[0] == Info.COMMENT 
        assert(l == Info.TITULO)

        # Guardamos el texto del titulo.
        self.titulo = finp.readline().strip()
        logging.info('<Titulo>: %s' % self.titulo)

        # Buscamos la siguiente etiqueta.
        ignorar = True
        while ignorar:
            l = finp.readline().strip()
            ignorar = len(l) == 0 or l[0] == Info.COMMENT
        
        # Ahora revisamos si existe encabezado para LaTeX. Si no 
        # hubiera encabezado, observe que entonces la variable 
        # estar\'ia en blanco.
        lista: List[str] = []
        continuar : bool
        if l == Info.ENCABEZADO:
            l = finp.readline()
            while l.find(Info.ABRIR) == -1:
                lista.append(l)
                l = finp.readline()
            logging.info('<Encabezado>')
            self.encabezado = '%s\n' % ''.join(lista).strip()
            logging.info(self.encabezado)
        else:
            self.encabezado = ''

        # Revisamos si son las instrucciones. Pueden abarcar varias 
        # l\'ineas de texto. Si no hubiera instrucciones, observe que
        # entonces la variable estar\'ia en blanco.
        lista = []
        if l.strip() == Info.INSTRUCCIONES:
            l = finp.readline()
            while l.find(Info.ABRIR) == -1:
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
        assert(l.startswith(Info.LSECCION))
        counter = 0
        self.secciones = [];
        es_aleatorio: bool = False
        while l.startswith(Info.LSECCION):
            l = l.strip(Info.STRIP)
            counter += 1
            logging.info('%d : Llamando a seccion ...' % counter)
            es_aleatorio = parserPPP.derecha_igual(l, 'orden') == 'aleatorio'
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

    def get_numPreguntas(self) -> List[int]:
        """ 
        Devuelve el n\'umero de preguntas por cada una de las secciones. 
        """
        lista: List[int] = []
        for cada in self.secciones:
            lista.append(cada.get_numPreguntas())
        return lista
