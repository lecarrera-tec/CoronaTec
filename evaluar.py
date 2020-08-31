#!/usr/bin/env python

import logging
import math
import os
import random
import sys
from typing import List, Dict

import Info
import latex
from ppp import PPP
from respuesta import Respuesta
from seccion import Seccion

"""
Funci\'on que realiza la evaluaci\'on de la prueba. 

Se espera como argumentos el archivo ppp, la carpeta con las listas de 
los estudiantes (opcionalmente puede ser solamente un archivo de solo un 
grupo), y el archivo `.csv` de las respuestas. 

De manera opcional se puede dar el \'indice de repetici\'on del examen. Esto 
es para que genere un examen diferente con el mismo n\'umero de carnet.
"""

logging.basicConfig(filename='_evaluar.log', level=logging.DEBUG, filemode='w')


# Estructura de la funci\'on.
#
# A. Se determina si el n\'umero de argumentos dados es el requerido.
#
# B. Se lee el \'indice de repetici\'on del examen, si es que se incluy\'o.
#    Si no, 0 es el valor predeterminado.
#
# C. Se lee la estructura general de la prueba.
#
# D. Se genera un diccionario con las respuestas. La clave es el n\'umero 
#    de carnet, y el valor respectivo corresponde a las respuestas como 
#    una lista de strings.
#
# E. El usuario pas\'o un solo archivo `.csv` o una carpeta donde debe
#    haber uno o m\'as archivos `.csv`. Se genera una lista del path a 
#    cada uno de los archivos.
#
# F. Se trabaja ahora grupo por grupo. Aqu\'i se inicia un archivo .pdf
#    donde se van a guardar las notas de los estudiantes para dar a cada
#    profesor.
#
#    F. i) Se abre el archivo del grupo, y se trabaja con cada 
#          estudiante.
#
#          1. Se obtiene el n\'umero de carnet. Si el n\'umero de carnet 
#             *no* se encuentra en el diccionario, se especifica en el 
#             archivo de notas, y se sigue con el siguiente estudiante.
#          2. Se genera la lista con las Respuesta's, y se califica.

#-----------------------------------------------------------------------
# A. Verificando el n\'umero de argumentos.
#-----------------------------------------------------------------------
# Si no se tienen la cantidad de argumentos correcta, se sale.
if len(sys.argv) < 4 or len(sys.argv) > 5:
    print('%s%s%s' % (
            'Se espera como argumentos el archivo ppp, la carpeta con las \n',
            'listas de los estudiantes. y el archivo `.csv` de las respuestas,\n',
            'y de manera opcional el \'indice de repetici\'on del examen.\n'))
    sys.exit()

#-----------------------------------------------------------------------
# B. \'Indice de repetici\'on. 0 es el valor predeterminado.
#-----------------------------------------------------------------------
indRepeticion: int = 0
if len(sys.argv) == 5:
    indRepeticion = int(sys.argv[4])
    assert(indRepeticion < len(Info.BY_SHIFT))

#-----------------------------------------------------------------------
# C. Estructura general del examen.
#-----------------------------------------------------------------------
examen = PPP(sys.argv[1])

#-----------------------------------------------------------------------
# D. Se genera el diccionario de las respuestas.
#-----------------------------------------------------------------------
assert(sys.argv[3].endswith('.csv'))
try:
    fresp = open(sys.argv[3])
except:
    logging.critical('No se pudo abrir el archivo con las respuestas.')
    sys.exit()

# Separamos el archivo l\'inea por l\'inea, y lo cerramos.
lineas: List[str] = fresp.readlines()
fresp.close()

totalPts: int = examen.get_puntaje()

# Se elimina la primera l\'inea, que es la informaci\'on de las columnas
# del archivo.
lineas.pop(0)
texto: str
cols: List[str]
# Diccionario!!!
todxs: Dict[int, List[str]] = {}
for fila in lineas:
    # Eliminamos el final de l\'inea y las comillas que pone Google por 
    # default.
    texto = fila.rstrip().replace('"', '')
    if len(texto) == 0:
        continue
    # Dada una fila, separamos los elementos de cada columna.
    cols = texto.split(',')
    # Agregamos la llave y le asignamos las respuestas. Tiene la 
    # caracter\'istica que si aparece el mismo carnet, toma como respuesta 
    # la versi\'on m\'as reciente, ya que google da las respuestas ordenadas 
    # por fecha.
    # Ignoramos el primer elemento (cols[0]) porque se refiere a la 
    # fecha y hora de env\'io de la prueba.
    # TODO Especificar hora de finalizaci\'on, para que cualquier 
    # evalluaci\'on registrada despu\'es de dicha hora, se informe de
    # alguna manera.
    todxs[int(cols[1])] = cols[2:]

#-----------------------------------------------------------------------
# E. Se genera la lista con las listas de los grupos dados.
#-----------------------------------------------------------------------
lestudiantes: List[str] = []
path: str = sys.argv[2]
if path.endswith('.csv'):
    # El argumento dado no fue una carpeta, si no fue solo una lista.
    lestudiantes = [sys.argv[2]]
else:
    # Si no fue un archivo .csv, suponemos que es una carpeta.
    try:
        listdir = os.listdir(path)
    except:
        logging.critical('%s "%s" %s' % (
            'No se pudo abrir carpeta', 
            sys.argv[2],
            'con las listas de estudiantes.'))
        sys.exit()
    if not path.endswith('/'):
        path = '%s/' % path
    for me in listdir:
        if me.endswith('.csv'):
            lestudiantes.append('%s%s' % (path, me))

#-----------------------------------------------------------------------
# E. Se trabaja grupo por grupo.
#-----------------------------------------------------------------------
carpeta: str    # Carpeta donde se guardan los informes y la nota.
filename: str 
lista: List[str]
linea: str    # Un estudiante de la lista.
idstr: str    # String del identificador del estudiante (# de carnet).
separar: List[str]   # Separar info del estudiante.
#@ Para construir el informe en latex. El encabezado es el mismo para
#@ todos los grupos.
numPreguntas: List[int] = examen.get_numPreguntas()
encabezado: str = latex.get_encabezadoInforme(numPreguntas)
for path in lestudiantes:
    logging.debug('PATH = %s\n' % path)
    # Carpeta donde se van a guardar los pdf's de los ex\'amenes.
    lista = path.rsplit(sep='/', maxsplit=1)
    filename = lista[1].rsplit(sep='.', maxsplit=1)[0]
    carpeta = '%s/%s' % (lista[0], filename.upper())
    if not os.path.exists(carpeta):
        os.mkdir(carpeta)
    
    # Se lee el archivo de los estudiantes.
    try:
        finput = open(path, 'r')
    except:
        logging.error('No se pudo abrir lista "%s"' % path)
        continue

    # Se separa la lista por estudiante.
    Lista: List[str] = finput.readlines()
    finput.close()
    
    # Ahora se trabaja con cada estudiante de la Lista.
    llatex: List[str] = []
    for linea in Lista:
        logging.debug('Nueva respuesta.')
        respuestas: List[Respuesta] = []
        # Separamos el n\'umero de identificaci\'on del resto del nombre.
        # ##-id-##, <apellidos/nombres>, xxxxx
        separar = linea.split(',')
        idstr = separar[0].strip()
        nombre = ' '.join([palabra.capitalize() 
                             for palabra in separar[1].strip().split()])
        #@
        izq: str = '    %s & %s' % (idstr, nombre)
        der: List[str] = []

        # Localizo las respuestas del estudiante, y contin\'uo si no est\'a.
        mias: List[str] = todxs.get(int(idstr), [])
        if len(mias) == 0:
            llatex.append('%s 0 & 0%s \\\\\n' 
                             % (izq, sum(numPreguntas) * ' & --'))
            continue
    
        # Se inicializa la semilla usando el identificador multiplicado 
        # por una constante, seg\'un el \'indice de repetici\'on dado.
        seed = Info.BY_SHIFT[indRepeticion] * int(idstr)
        logging.debug('random.seed: %d' % seed)
        random.seed(seed)
    
        # Se comienzan a agregar las instancias de los objetos de tipo
        # Respuesta.
        for seccion in examen.secciones:
            respuestas += seccion.get_respuestas()

        # Ahora probamos a calificar.
        assert(len(respuestas) == len(mias))
        total: float = 0.0
        for elem in mias:
            pts = respuestas.pop(0).calificar(elem.strip())
            if isinstance(pts[0], int) or pts[0].is_integer():
                tempStr = '%d' % pts[0]
            else:
                tempStr = '%.2f' % 0.01 * math.floor(100 * pts[0])
            der.append(' & $\\nicefrac{%s}{%d}$' % (tempStr, pts[1]))
            total += pts[0]
        llatex.append('%s & \\textbf{%.2f} & %d %s \\\\\n'
                % (izq, 0.01 * math.ceil(1e4 * total / totalPts), 
                    total, ''.join(der)))
    llatex.append('    \\bottomrule\n')
    llatex.append('  \\end{tabular}\n')
    llatex.append('\\end{center}\n')
    llatex.append('\\end{document}\n')
    fout = open('%s.tex' % filename, 'w')
    fout.write(encabezado)
    fout.writelines(llatex)
    fout.close()
    
    # Se genera el pdf.
    os.system('pdflatex %s' % filename)
    logging.debug('Fin de examen\n')

    # Se mueve el pdf a la carpeta respectiva, y se eliminan el 
    # resto de los archivos.
    os.replace('%s.pdf' % filename, '%s/%s.pdf' % (carpeta, filename))
    lista = os.listdir('./')
    for fname in lista:
        if fname.startswith(filename):
            os.remove(fname)
