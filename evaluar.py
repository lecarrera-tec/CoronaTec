#!/usr/bin/env python

import logging
import math
import os
import random
import sys
from typing import List, Dict, Tuple

import Info
import latex
from ppp import PPP
from respuesta import Respuesta
from seccion import Seccion
import tabla

import xlsxwriter

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
# B. Se lee el \'indice de repetici\'on del examen, si es que se 
#    incluy\'o. Si no, 0 es el valor predeterminado.
#
# C. Se lee la estructura general de la prueba.
#
# D. Se genera un diccionario con las respuestas. La clave es el 
#    n\'umero de carnet, y el valor respectivo corresponde a las 
#    respuestas como una lista de strings.
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

# Se descartan la l\'ineas iniciales en caso de ser necesario.
for i in range(Info.CSV_IROW):
    lineas.pop(0)
texto: str
cols: List[str]
# Diccionario!!!
todxs: Dict[str, List[str]] = {}
for fila in lineas:
    # Se eliminan espacios en blanco y las comillas, en caso que hubieran.
    texto = fila.rstrip().replace('"', '')
    if len(texto) == 0:
        continue
    # Dada una fila, separamos los elementos de cada columna.
    cols = texto.split(Info.CSV_SEP)
    # Agregamos la llave y le asignamos las respuestas. Tiene la 
    # caracter\'istica que si aparece el mismo carnet una segunda vez,
    # la respuesta es la versi\'on m\'as reciente. No pareciera que
    # importe.
    # Ignoramos las primeras columnas, damos el \'indice de la columna
    # de la llave, y la columna inicial de las respuestas (y asumimos
    # que las respuestas son hasta el final, al menos que la \'ultima 
    # columna sea la que corresponda al # de carnet).
    if Info.CSV_IKEY == -1:
        todxs[cols[Info.CSV_IKEY]] = cols[Info.CSV_ICOL:-1]
    else:
        todxs[cols[Info.CSV_IKEY]] = cols[Info.CSV_ICOL:]

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
carpeta: str    # Carpeta donde se guardan los reportes y la nota.
filename: str 
lista: List[str]
linea: str    # Un estudiante de la lista.
idstr: str    # String del identificador del estudiante (# de carnet).
separar: List[str]   # Separar info del estudiante.
numPreguntas: List[int] = examen.get_numPreguntas()
todasResp: List[Tuple[str, List[Tuple[str, Respuesta]]]]
todosPuntos: List[Tuple[str, List[Tuple[float, int]]]] 
for path in lestudiantes:
    todasResp = []
    todosPuntos = []
    encabezado: str = latex.get_encabezadoInforme(numPreguntas)
    logging.debug('PATH = %s\n' % path)
    # Carpeta donde se van a guardar las notas y el reporte
    # (es la misma carpeta donde se generaron los ex\'amenes en pdf)
    lista = path.rsplit(sep='/', maxsplit=1)
    filename = lista[1].rsplit(sep='.', maxsplit=1)[0]
    carpeta = '%s/%s' % (lista[0], filename.upper())
    if not os.path.exists(carpeta):
        os.mkdir(carpeta)

    #@ Para construir el archivo de notas.
    notasBook = xlsxwriter.Workbook('%s/%s_notas.xlsx' % (carpeta, filename))
    notasSheet = notasBook.add_worksheet()
    bold = notasBook.add_format({'bold': 1})
    tabla.encabezadoNotas(notasSheet, sum(numPreguntas))

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
    irow: int = 0
    for linea in Lista:
        irow = irow + 1
        logging.debug('Nueva respuesta.')
        respuestas: List[Respuesta] = []
        # Separamos el n\'umero de identificaci\'on del resto del nombre.
        # ##-id-##, <apellidos/nombres>, xxxxx
        separar = linea.split(',')
        idstr = separar[0].strip()
        nombre = ' '.join([palabra.capitalize() 
                             for palabra in separar[1].strip().split()])
        #@
        notasSheet.write(irow, 0, idstr)
        notasSheet.write(irow, 1, nombre)

        # Localizo las respuestas del estudiante
        misResp: List[str] = todxs.get(idstr, [])
        # Si no tiene respuestas, lleno el excel de ceros, y calculo
        # la suma y la nota igual. Sigo con el siguiente.
        if len(misResp) == 0:
            tabla.notasNull(notasSheet, sum(numPreguntas), irow)
            #@ Se suman los puntos ;)
            notasSheet.write(irow, 3, '=SUM(E%d:%c%d)' % (irow + 1, 
                                chr(ord('E') + sum(numPreguntas) - 1), irow + 1))
            #@ y se calcula la nota
            notasSheet.write(irow, 2, '= 100 * D%d / %d' % (irow + 1, totalPts), bold)
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
        assert(len(respuestas) == len(misResp))
        unir: List[Tuple[str,Respuesta]] = []
        puntos: List[Tuple[float, int]] = []
        for i in range(len(misResp)):
            unir.append((misResp[i], respuestas[i]))
        todasResp.append((idstr[-6:], unir))
        icol: int = 3
        for elem, resp in unir:
            icol += 1
            pts = resp.calificar(elem.strip())
            puntos.append(pts)
            #@ Se escribe el puntaje obtenido en el excel.
            notasSheet.write(irow, icol, pts[0])
        todosPuntos.append((idstr[-6:], puntos))
        #@ Se suman los puntos
        notasSheet.write(irow, 3, '=SUM(E%d:%c%d)' % (irow + 1, 
                            chr(ord('E') + sum(numPreguntas) - 1), irow + 1))
        #@ y se calcula la nota
        notasSheet.write(irow, 2, '= 100 * D%d / %d' % (irow + 1, totalPts), bold)
    notasBook.close()
    #< Para construir el archivo del reporte
    infoBook = xlsxwriter.Workbook('%s/%s_reporte.xlsx' % (carpeta, filename))
    infoSheet = infoBook.add_worksheet()
    bold = infoBook.add_format({'bold': 1})
    infoSheet.set_column('A:Z', 10)
    todasResp.sort(key=lambda x: x[0])
    todosPuntos.sort(key=lambda x: x[0])
    irow = 0
    assert(len(todasResp) == len(todosPuntos))
    for i in range(len(todasResp)):
        resps = todasResp[i]
        puntos = todosPuntos[i][1]
        infoSheet.write(irow, 0, resps[0])
        infoSheet.write(irow+2, 0, 'Correcta')
        icol = 1
        for j in range(len(resps[1])):
            temp = resps[1][j]
            infoSheet.write(irow,   icol, temp[0])
            infoSheet.write(irow+1, icol, puntos[j][0])
            infoSheet.write(irow+2, icol, temp[1].textoResp())
            infoSheet.write(irow+3, icol, puntos[j][1])
            icol += 1
        #@ Se suman los puntos
        infoSheet.write(irow+1, icol, '=SUM(B%d:%c%d)' % (irow + 2, 
                            chr(ord('A') + icol - 1), irow + 2))
        #@ y se calcula la nota
        infoSheet.write(irow+1, icol+1, '= 100 * %c%d / %c%d' % 
                          (chr(ord('A') + icol), irow+2, 
                              chr(ord('A') + icol), irow+4), bold)
        infoSheet.write(irow+3, icol, '=SUM(B%d:%c%d)' % (irow+4, 
                            chr(ord('A') + icol - 1), irow + 4))
        infoSheet.write(irow+3, icol+1, 100)

        irow += 5
    infoBook.close()
    logging.debug('Fin de examen\n')
