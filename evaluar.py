#!/usr/bin/env python

import logging
import math
import os
import random
import sys
from typing import List, Dict, Tuple

import Info
import fmate
from ppp import PPP
from respuesta import Respuesta
import tabla

import xlsxwriter

"""
Función que realiza la evaluación de la prueba.

Se espera como argumentos el archivo ppp, la carpeta con las listas de
los estudiantes (opcionalmente puede ser solamente un archivo de solo un
grupo), y el archivo `.csv` de las respuestas.

De manera opcional se puede dar el índice de repetición del examen. Esto
es para que genere un examen diferente con el mismo número de carnet.
"""


def __imprimir_reporte__(carpeta, filename, todasResp, todosPuntos):
    infoBook = xlsxwriter.Workbook('%s/%s_reporte.xlsx' % (carpeta, filename))
    infoSheet = infoBook.add_worksheet()
    bold = infoBook.add_format({'bold': 1})
    infoSheet.set_column('A:Z', 10)
    todasResp.sort(key=lambda x: x[0])
    todosPuntos.sort(key=lambda x: x[0])
    irow = 0
    assert(len(todasResp) == len(todosPuntos))
    # List[(id_est, List[resp_est, Respuesta])]
    resps: Tuple[str, List[Tuple[str, Respuesta]]]
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
            valor = temp[1].get_respuesta()
            if isinstance(valor, float):
                cifras = 1 + math.ceil(-math.log10(temp[1].get_error()))
                valor = fmate.digSignif(valor, cifras)
            infoSheet.write(irow+2, icol, valor)
            infoSheet.write(irow+3, icol, puntos[j][1])
            icol += 1
        # @ Se suman los puntos
        formula = '=SUM(B%d:%c%d)' % (irow+2, chr(ord('A')+icol-1), irow+2)
        infoSheet.write(irow+1, icol, formula)
        # @ y se calcula la nota
        formula = '= 100 * %c%d / %c%d'\
                  % (chr(ord('A') + icol),
                     irow+2,
                     chr(ord('A') + icol),
                     irow+4)
        infoSheet.write(irow+1, icol+1, formula, bold)
        formula = '=SUM(B%d:%c%d)' % (irow+4, chr(ord('A')+icol-1), irow+4)
        infoSheet.write(irow+3, icol, formula)
        infoSheet.write(irow+3, icol+1, 100)
        irow += 5
    infoBook.close()


logging.basicConfig(filename='_evaluar.log', level=logging.DEBUG, filemode='w')
# Estructura de la función.
#
# A. Se determina si el número de argumentos dados es el requerido.
#
# B. Se lee el índice de repetición del examen, si es que se
#    incluyó. Si no, 0 es el valor predeterminado.
#
# C. Se lee la estructura general de la prueba.
#
# D. Se genera un diccionario con las respuestas. La clave es el
#    número de carnet, y el valor respectivo corresponde a las
#    respuestas como una lista de strings.
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

# ----------------------------------------------------------------------
# A. Verificando el número de argumentos.
# ----------------------------------------------------------------------
# Si no se tienen la cantidad de argumentos correcta, se sale.
if len(sys.argv) < 4 or len(sys.argv) > 5:
    print('%s%s%s' % (
            'Se espera como argumentos el archivo ppp, la carpeta con las \n',
            'listas de estudiantes. y el archivo `.csv` de las respuestas,\n',
            'y de manera opcional el índice de repetición del examen.\n'))
    sys.exit()

# ----------------------------------------------------------------------
# B. Índice de repetición. 0 es el valor predeterminado.
# ----------------------------------------------------------------------
indRepeticion: int = 0
if len(sys.argv) == 5:
    indRepeticion = int(sys.argv[4])
    assert(indRepeticion < len(Info.BY_SHIFT))

# ----------------------------------------------------------------------
# C. Estructura general del examen.
# ----------------------------------------------------------------------
examen = PPP(sys.argv[1])

# ----------------------------------------------------------------------
# D. Se genera el diccionario de las respuestas.
# ----------------------------------------------------------------------
assert(sys.argv[3].endswith('.csv'))
try:
    fresp = open(sys.argv[3])
except FileNotFoundError:
    logging.critical('No se pudo abrir el archivo con las respuestas.')
    sys.exit()

# Separamos el archivo línea por línea, y lo cerramos.
lineas: List[str] = fresp.readlines()
fresp.close()

totalPts: int = examen.get_puntaje()

# Se descartan la líneas iniciales en caso de ser necesario.
for i in range(Info.CSV_IROW):
    lineas.pop(0)
texto: str
cols: List[str]
# Diccionario!!!
todxs: Dict[str, Tuple[List[str], str]] = {}
for fila in lineas:
    # Se eliminan espacios en blanco y las comillas, en caso que
    # hubieran.
    texto = fila.rstrip().replace('"', '')
    if len(texto) == 0:
        continue
    # Dada una fila, separamos los elementos de cada columna.
    cols = texto.split(Info.CSV_SEP)
    # Agregamos la llave y le asignamos las respuestas. Tiene la
    # característica que si aparece el mismo carnet una segunda vez,
    # la respuesta es la versión más reciente. No pareciera que
    # importe.
    # Ignoramos las primeras columnas, damos el índice de la columna
    # de la llave, y la columna inicial de las respuestas (y asumimos
    # que las respuestas son hasta el final, al menos que la última
    # columna sea la que corresponda al # de carnet).
    if Info.CSV_IKEY == -1:
        todxs[cols[Info.CSV_IKEY]] = (cols[Info.CSV_ICOL:-1],
                                      cols[Info.CSV_INAME])
    else:
        todxs[cols[Info.CSV_IKEY]] = (cols[Info.CSV_ICOL:],
                                      cols[Info.CSV_INAME])

# ----------------------------------------------------------------------
# E. Se genera la lista con las listas de los grupos dados.
# ----------------------------------------------------------------------
lestudiantes: List[str] = []
path: str = sys.argv[2]
if path.endswith('.csv'):
    # El argumento dado no fue una carpeta, si no fue solo una lista.
    lestudiantes = [sys.argv[2]]
else:
    # Si no fue un archivo .csv, suponemos que es una carpeta.
    try:
        listdir = os.listdir(path)
    except FileNotFoundError:
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

# ----------------------------------------------------------------------
# E. Se trabaja grupo por grupo.
# ----------------------------------------------------------------------
carpeta: str    # Carpeta donde se guardan los reportes y la nota.
filename: str
formula: str
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
    logging.debug('PATH = %s\n' % path)
    # Carpeta donde se van a guardar las notas y el reporte
    # (es la misma carpeta donde se generaron los exámenes en pdf)
    lista = path.rsplit(sep='/', maxsplit=1)
    filename = lista[1].rsplit(sep='.', maxsplit=1)[0]
    carpeta = '%s/%s' % (lista[0], filename.upper())
    if not os.path.exists(carpeta):
        os.mkdir(carpeta)

    # @ Para construir el archivo de notas.
    notasBook = xlsxwriter.Workbook('%s/%s_notas.xlsx' % (carpeta, filename))
    notasSheet = notasBook.add_worksheet()
    bold = notasBook.add_format({'bold': 1})
    tabla.encabezadoNotas(notasSheet, sum(numPreguntas))

    # Se lee el archivo de los estudiantes.
    try:
        finput = open(path, 'r')
    except FileNotFoundError:
        logging.error('No se pudo abrir lista "%s"' % path)
        continue

    # Se separa la lista por estudiante.
    Lista: List[str] = finput.readlines()
    finput.close()

    # Ahora se trabaja con cada estudiante de la Lista.
    irow: int = 0
    for linea in Lista:
        irow = irow + 1
        logging.debug('Nueva respuesta: %s' % linea)
        respuestas: List[Respuesta] = []
        # Separamos el número de identificación del resto del nombre.
        # ##-id-##, <apellidos/nombres>, xxxxx
        separar = linea.split(',')
        idstr = separar[0].strip()
        nombre = ' '.join([palabra.capitalize()
                           for palabra in separar[1].strip().split()])
        # @
        notasSheet.write(irow, 0, idstr)
        notasSheet.write(irow, 1, nombre)

        # Localizo las respuestas del estudiante
        par: Tuple[List[str], str] = todxs.get(idstr, ([], 'ausente'))
        misResp: List[str] = par[0]
        # Si no tiene respuestas, lleno el excel de ceros, y calculo
        # la suma y la nota igual. Sigo con el siguiente.
        if len(misResp) == 0:
            tabla.notasNull(notasSheet, sum(numPreguntas), irow)
            # @ Se suman los puntos ;)
            formula = '=SUM(F%d:%c%d)'\
                      % (irow + 1,
                         chr(ord('F') + sum(numPreguntas) - 1),
                         irow + 1)
            notasSheet.write(irow, 4, formula)
            # @ y se calcula la nota
            formula = '= 100 * E%d / %d' % (irow + 1, totalPts)
            notasSheet.write(irow, 3, formula, bold)
            notasSheet.write(irow, 2, 'ausente')
            continue

        # Se imprime el usuario si no coincide con el nombre
        con_nombre = set(nombre.split())
        usuario = [palabra.capitalize() for palabra in par[1].strip().split()]
        if not con_nombre == set(usuario):
            notasSheet.write(irow, 2, ' '.join(usuario))
        # Se inicializa la semilla usando el identificador multiplicado
        # por una constante, según el índice de repetición dado.
        seed = Info.BY_SHIFT[indRepeticion] * int(idstr)
        logging.debug('numero de carnet: %s' % idstr)
        logging.debug('Random: seed = %d' % seed)
        random.seed(seed)

        # Se comienzan a agregar las instancias de los objetos de tipo
        # Respuesta.
        for seccion in examen.secciones:
            respuestas += seccion.get_respuestas()

        # Ahora probamos a calificar.
        assert(len(respuestas) == len(misResp))
        unir: List[Tuple[str, Respuesta]] = []
        puntos: List[Tuple[float, int]] = []
        unir = [(misResp[i], respuestas[i]) for i in range(len(misResp))]
        # Se cambia el identificador a partir de acá.
        idx = 1 + nombre.find(' ')
        idstr = '%s%s' % (idstr[-6:],
                          nombre[idx:idx+5].lower().replace(' ', '_'))
        todasResp.append((idstr, unir))
        icol: int = 4
        for elem, resp in unir:
            icol += 1
            pts = resp.calificar(elem.strip())
            puntos.append(pts)
            # @ Se escribe el puntaje obtenido en el excel.
            notasSheet.write(irow, icol, pts[0])
        todosPuntos.append((idstr, puntos))
        # @ Se suman los puntos
        formula = '=SUM(F%d:%c%d)'\
                  % (irow + 1,
                     chr(ord('F') + sum(numPreguntas) - 1),
                     irow + 1)
        notasSheet.write(irow, 4, formula)
        # @ y se calcula la nota
        formula = '= 100 * E%d / %d' % (irow + 1, totalPts)
        notasSheet.write(irow, 3, formula, bold)
    notasBook.close()
    # < Para construir el archivo del reporte
    __imprimir_reporte__(carpeta, filename, todasResp, todosPuntos)
    logging.debug('Fin de evaluación.\n')
