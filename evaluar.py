#!/usr/bin/env python

import logging
import os
import random
import sys
from typing import List

import info
from ppp import PPP
from seccion import Seccion

"""
Función que realiza la evaluación de la prueba. 

Se espera como argumentos el archivo ppp, la carpeta con las listas de 
los estudiantes (opcionalmente puede ser solamente un archivo de solo un 
grupo), y el archivo `.csv` de las respuestas. 

De manera opcional se puede dar el índice de repetición del examen. Esto 
es para que genere un examen diferente con el mismo número de carnet.
"""

logging.basicConfig(filename='_evaluar.log', level=logging.DEBUG, filemode='w')


# Estructura de la función.
#
# A. Se determina si el número de argumentos dados es el requerido.
#
# B. Se lee el índice de repetición del examen, si es que se incluyó.
#    Si no, 0 es el valor predeterminado.
#
# C. Se lee la estructura general de la prueba.
#
# D. Se genera un diccionario con las respuestas. La clave es el número 
#    de carnet, y el valor respectivo corresponde a las respuestas como 
#    una lista de strings.
#
# E. El usuario pasó un solo archivo `.csv` o una carpeta donde debe
#    haber uno o más archivos `.csv`. Se genera una lista del path a 
#    cada uno de los archivos.
#
# F. Se trabaja ahora grupo por grupo. Aquí se inicia un archivo .pdf
#    donde se van a guardar las notas de los estudiantes para dar a cada
#    profesor.
#
#    F. i) Se abre el archivo del grupo, y se trabaja con cada 
#          estudiante.
#
#          1. Se obtiene el número de carnet. Si el número de carnet 
#             *no* se encuentra en el diccionario, se especifica en el 
#             archivo de notas, y se sigue con el siguiente estudiante.
#          2. Se genera la lista con las Respuesta's, y se califica.

#-----------------------------------------------------------------------
# A. Verificando el número de argumentos.
#-----------------------------------------------------------------------
# Si no se tienen la cantidad de argumentos correcta, se sale.
if len(sys.argv) < 4 or len(sys.argv) > 5:
    print('%s%s%s' % (
            'Se espera como argumentos el archivo ppp, la carpeta con las \n',
            'listas de los estudiantes. y el archivo `.csv` de las respuestas,\n',
            'y de manera opcional el índice de repetición del examen.\n'))
    sys.exit()

#-----------------------------------------------------------------------
# B. Índice de repetición. 0 es el valor predeterminado.
#-----------------------------------------------------------------------
ind_repeticion: int = 0
if len(sys.argv) == 5:
    ind_repeticion = int(sys.argv[4])
    assert(ind_repeticion < len(info.BY_SHIFT))

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

# Separamos el archivo línea por línea, y lo cerramos.
lineas: List[str] = fresp.readlines()
fresp.close()

# Se elimina la primera línea, que es la información de las columnas
# del archivo.
lineas.pop(0)
texto: str
cols: List[str]
# Diccionario!!!
todxs = {}
for fila in lineas:
    # Eliminamos el final de línea y las comillas que pone Google por 
    # default.
    texto = fila.rstrip().replace('"', '')
    if len(texto) == 0:
        continue
    # Dada una fila, separamos los elementos de cada columna.
    cols = texto.split(',')
    # Agregamos la llave y le asignamos las respuestas. Tiene la 
    # característica que si aparece el mismo carnet, toma como 
    # respuesta la versión más reciente, ya que google da las
    # respuestas ordenadas por fecha.
    # Ignoramos el primer elemento (cols[0]) porque se refiere a la 
    # fecha y hora de envío de la prueba.
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
linea : str    # Un estudiante de la lista.
idstr : str    # String del identificador del estudiante (# de carnet).
separar : List[str]   # Separar info del estudiante.
for path in lestudiantes:
    logging.debug('PATH = %s\n' % path)
    # Carpeta donde se van a guardar los pdf's de los exámenes.
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
    for linea in Lista:
        logging.debug('Nueva respuesta.')
        respuestas = []
        # Separamos el número de identificación del resto del nombre.
        # ##-id-##, <apellidos/nombres>, xxxxx
        separar = linea.split(',')
        idstr = separar[0].strip()
        nombre = separar[1].strip()

        # Localizo las respuestas del estudiante, y continúo si no está.
        mias = todxs.get(int(idstr))
        if mias == None:
            # TODO Llenar la información en el archivo de notas.
            continue
    
        # Se inicializa la semilla usando el identificador multiplicado 
        # por una constante, según el índice de repetición dado.
        random.seed(info.BY_SHIFT[ind_repeticion] * int(idstr))
    
        # Se comienzan a agregar las instancias de los objetos de tipo
        # Respuesta.
        for seccion in examen.secciones:
            respuestas += seccion.get_respuestas()

        # Ahora probamos a calificar.
        assert(len(respuestas) == len(mias))
        total: int = 0
        for elem in mias:
            pts = respuestas.pop(0).calificar(elem.strip())
            total += pts
        print('Total de puntos = %d' % total)
    
##    # Se imprimen las notas de los estudiantes.
##    filename = idstr[-6:]
##    fout = open('%s.tex' % filename, 'w')
##    fout.write(encabezado)
##    fout.writelines(tex)
##    fout.close();
##
##    # Se genera el pdf.
##    os.system('pdflatex %s' % filename)
##    os.system('pdflatex %s' % filename)
##    logging.debug('Fin de examen\n')
##
##    # Se mueve el pdf a la carpeta respectiva, y se eliminan el 
##    # resto de los archivos.
##    os.replace('%s.pdf' % filename, '%s/%s.pdf' % (carpeta, filename))
##    lista = os.listdir('./')
##    for fname in lista:
##        if fname.startswith(filename):
##            os.remove(fname)
