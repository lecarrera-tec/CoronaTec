from typing import List

from seccion import Seccion
import info
import parser
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

    def __init__(self, filename : str) :
        """
        Constructor. Recibe como argumento la direccion un archivo 
        de tipo .ppp

        Devuelve la estructura principal, y la estructura anidada
        de cada una de las secciones.

        Se definen las variables:
            - path          : direcci\'on a la carpeta de la prueba.
                              Se requiere porque la direcci\'on de las
                              preguntas es relativa a dicha carpeta.
            - curso         : Nombre del curso.
            - titulo        : T\'itulo de la prueba.
            - instrucciones : Instrucciones de la prueba.
            - encabezado    : Encabezado a agregar a \LaTeX
            - secciones     : Una lista de instancias de la clase 
                              seccion
        """
        # Definimos el puntaje total como 0, de manera temporal.
        self.puntaje = 0

        # Definimos el path local por default, pero si la direccion
        # dada no es un archivo en el directorio actual, entonces 
        # vamos a guardar el path al archivo, porque la referencia 
        # a los archivos de las preguntas es relativa al path del 
        # archivo principal. 
        # Warning! Estamos pensando en linux!
        self.path = './'
        idx = filename.rfind('/')
        if idx > 0:
            self.path = filename[0:idx+1]

        # Vamos a leer el archivo linea x linea. Por lo general se van 
        # a ignorar lineas en blanco y lineas que comiencen con el 
        # caracter de comentario.
        finp = open(filename, 'r')

        # Lo primero que deber\'iamos encontrar en el archivo es el 
        # nombre del curso. Buscamos primero la etiqueta.
        ignorar = True
        while ignorar:
            l = finp.readline().strip()
            ignorar = len(l) == 0 or l[0] == info.COMMENT 
        assert(l == info.CURSO)

        # Guardamos el texto del nombre del curso.
        self.curso = finp.readline().strip()
        print('<Curso> : ' + self.curso)

        # Luego deber\'ia seguir el t\'itulo de la prueba. Buscamos la 
        # etiqueta respectiva.
        ignorar = True
        while ignorar:
            l = finp.readline().strip()
            ignorar = len(l) == 0 or l[0] == info.COMMENT 
        assert(l == info.TITULO)

        # Guardamos el texto del titulo.
        self.titulo = finp.readline().strip()
        print('<Titulo> : ' + self.titulo)

        # Buscamos la siguiente etiqueta.
        ignorar = True
        while ignorar:
            l = finp.readline().strip()
            ignorar = len(l) == 0 or l[0] == info.COMMENT
        
        # Revisamos si son las instrucciones. Pueden abarcar varias 
        # l\'ineas de texto. Si no hubiera instrucciones, observe que
        # entonces la variable estar\'ia en blanco.
        self.instrucciones = []
        if l == info.INSTRUCCIONES:
            l = finp.readline()
            while l.find(info.ABRIR) == -1:
                self.instrucciones.append(l)
                l = finp.readline()

        # Ahora revisamos si existe encabezado para LaTeX. Si no 
        # hubiera instrucciones, observe que entonces la variable 
        # estar\'ia en blanco.
        self.encabezado = []
        if l == info.ENCABEZADO:
            l = finp.readline()
            while l.find(info.ABRIR) == -1:
                self.encabezado.append(l)
                l = finp.readline()

        # No queda de otra. Tienen que seguir las secciones.
        # Una lista de instancias.
        l = l.strip()
        assert(l.startswith(info.LSECCION))
        counter = 0
        self.secciones = [];
        while l.strip().startswith(info.LSECCION):
            counter += 1
            print(str(counter) + ' : Llamando a seccion ...')
            l = parser.extraer(l, 'orden')
            self.secciones.append(Seccion(finp, l == 'random'))
            l = finp.readline().strip()

    def get_puntaje(self) -> int:
        """
        Calcula el puntaje total de la prueba.
        """
        if self.puntaje == 0:
            for cada in self.secciones:
                self.puntaje += cada.get_puntaje()
        return self.puntaje

