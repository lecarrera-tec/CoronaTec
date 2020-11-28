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
Script que realiza la evaluación de la prueba.

Se espera como argumentos el archivo ppp, la carpeta con las listas de
los estudiantes (opcionalmente puede ser solamente un archivo de solo un
grupo), y el archivo `.csv` de las respuestas.

De manera opcional se puede dar el índice de repetición del examen. Esto
es para que genere un examen diferente con el mismo número de carnet.
"""


# TODO Mejorar documentación de método.
def __imprimir_reporte__(carpeta, filename, todasResp, todosPuntos):
    """ Imprime el reporte que se comparte a los estudiantes.
    """
    infoBook = xlsxwriter.Workbook('%s/%s_reporte.xlsx' % (carpeta, filename))
    infoSheet = infoBook.add_worksheet()
    bold = infoBook.add_format({'bold': 1})
    infoSheet.set_column('A:Z', 10)
    infoSheet.set_column('AA:AZ', 10)
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
                if valor.is_integer():
                    valor = int(valor)
                elif temp[1].get_error() > 0:
                    cifras = 1 + math.ceil(-math.log10(temp[1].get_error()))
                    valor = fmate.digSignif(valor, cifras)
            infoSheet.write(irow+2, icol, valor)
            infoSheet.write(irow+3, icol, puntos[j][1])
            icol += 1
        # Se suman los puntos
        letras = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ind1 = (icol - 1) // 26
        ind2 = (icol - 1) % 26
        if ind1 > 0:
            txtFormula = '%s%s' % (letras[ind1 - 1], letras[ind2])
        else:
            txtFormula = letras[ind2]
        formula = '=SUM(B%d:%s%d)' % (irow+2, txtFormula, irow+2)
        infoSheet.write(irow+1, icol, formula)
        # y se calcula la nota
        formula = '=SUM(B%d:%s%d)' % (irow+4, txtFormula, irow+4)
        infoSheet.write(irow+3, icol, formula)
        infoSheet.write(irow+3, icol+1, 100)
        ind1 = icol // 26
        ind2 = icol % 26
        if ind1 > 0:
            txtFormula = '%s%s' % (letras[ind1 - 1], letras[ind2])
        else:
            txtFormula = letras[ind2]
        formula = '= 100 * %s%d / %s%d'\
                  % (txtFormula, irow+2, txtFormula, irow+4)
        infoSheet.write(irow+1, icol+1, formula, bold)
        irow += 5
    infoBook.close()


def __nombre_es_llave__(nombre: str) -> str:
    """ Transforma el nombre en una llave única e igual.

    El problema es que la lista del TecDigital y la lista de estudiantec
    no coinciden. En la última, a veces intercambia un nombre con un
    apellido. Se deja todo en minúsculas, se eliminan las ñ's y se
    ordenan las palabras.
    """
    temp: List[str] = nombre.strip().split()
    temp = sorted([pp.lower().replace('ñ', 'n') for pp in temp])
    return '-'.join(temp)


def __comparar_usuario__(nombre, texto, notasSheet):
    # Se imprime el usuario si no coincide con el nombre
    ls_nombre = set([palabra.lower().replace('ñ', 'n')
                    for palabra in nombre.split()])
    usuario = [palabra.capitalize() for palabra in texto.strip().split()]
    ls_usuario = set([palabra.lower().replace('ñ', 'n')
                     for palabra in usuario])
    if not ls_nombre == ls_usuario:
        notasSheet.write(irow, 2, ' '.join(usuario))


def __calificar__(respuestas, misResp, nombre, idstr, todasResp,
                  todosPuntos, totalPts, sheet, irow, bold):
    assert(len(respuestas) == len(misResp))
    unir: List[Tuple[str, Respuesta]] = []
    puntos: List[Tuple[float, int]] = []
    unir = [(misResp[i], respuestas[i]) for i in range(len(misResp))]
    # Se cambia el identificador a partir de acá.
    # idx = 1 + nombre.find(' ')
    # idstr = '%s%s' % (idstr[-6:],
    #                   nombre[idx:idx+4].lower().replace(' ', '_'))
    idstr = '%s%s' % (nombre[:4].lower().replace(' ', '_'),
                         idstr[-6:])
    todasResp.append((idstr, unir))
    icol: int = 4
    for elem, resp in unir:
        icol += 1
        pts = resp.calificar(elem.strip())
        puntos.append(pts)
        # @ Se escribe el puntaje obtenido en el excel.
        sheet.write(irow, icol, pts[0])
    todosPuntos.append((idstr, puntos))
    # @ Se suman los puntos
    letras = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    icol = ord('F') + sum(numPreguntas) - 1 - ord('A')
    ind1 = icol // 26
    ind2 = icol % 26
    if ind1 > 0:
        txtFormula = '%c%c' % (letras[ind1 - 1], letras[ind2])
    else:
        txtFormula = letras[ind2]
    formula = '=SUM(F%d:%s%d)' % (irow + 1, txtFormula, irow + 1)
    sheet.write(irow, 4, formula)
    # @ y se calcula la nota
    formula = '= 100 * E%d / %d' % (irow + 1, totalPts)
    notasSheet.write(irow, 3, formula, bold)


try:
    Info.CSV_IKEY
except AttributeError:
    print('ERROR\n-----')
    print('Debe quitar el comentario en el archivo Info.py a alguna de las')
    print('dos definiciones de CSV_IKEY. El valor de -1 es cuando se utiliza')
    print('el número de carnet al final del formulario como identificador;')
    print('el valor de 4 es cuando se utiliza el nombre como identificador')
    print('cuando se utiliza una cuenta de Microsoft (estudiantec.cr)')
    sys.exit()


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
# Se escriben los elementos del nombre en orden alfabético como llave
# para el diccionario. Cada elemento es la lista de respuestas, junto
# con el correo, que es el identificador único del usuario en el
# formulario.
todxs: Dict[str, Tuple[List[str], str]] = {}
for fila in lineas:
    # Se eliminan espacios en blanco y las comillas, en caso que
    # hubieran.
    texto = fila.rstrip().replace('"', '')
    if len(texto) == 0:
        continue
    # Dada una fila, separamos los elementos de cada columna.
    cols = texto.split(Info.CSV_SEP)
    # Agregamos la llave y le asignamos las respuestas. Si se repite
    # la llave, se imprime la información en la salida.
    # Ignoramos las primeras columnas, damos el índice de la columna
    # de la llave, y la columna inicial de las respuestas (y asumimos
    # que las respuestas son hasta el final, al menos que la última
    # columna sea la que corresponda al # de carnet).

    # Se utiliza el # de carnet como llave.
    llave: str
    if Info.CSV_IKEY == -1:
        llave = cols[Info.CSV_IKEY]
        if llave in todxs:
            usuario = todxs[llave][1]
            print('%s tiene dos respuestas.' % llave)
            print('Verifique usuario: "%s" vs "%s"'
                  % (usuario, cols[Info.CSV_INAME]))
        todxs[cols[Info.CSV_IKEY]] = (cols[Info.CSV_ICOL:-1],
                                      cols[Info.CSV_INAME])
    else:
        llave = __nombre_es_llave__(cols[Info.CSV_INAME])
        if llave in todxs:
            print('\nAdvertencia\n-----------')
            print('%s ya existe. Compruebe que sea el mismo usuario.'
                  % cols[Info.CSV_INAME])
            usuario = todxs[llave][1]
            print('"%s" vs "%s"\n' % (usuario, cols[Info.CSV_EMAIL]))
        todxs[llave] = (cols[Info.CSV_ICOL:], cols[Info.CSV_EMAIL])

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
        logging.debug('Nueva respuesta: %s' % linea.strip())
        respuestas: List[Respuesta] = []
        # Separamos el número de identificación del resto del nombre.
        # ##-id-##, <apellidos/nombres>, xxxxx
        separar = linea.split(',')
        idstr = separar[0].strip()
        if Info.CSV_IKEY == -1:
            llave = idstr
        else:
            llave = __nombre_es_llave__(separar[1])
        nombre = ' '.join([palabra.capitalize()
                           for palabra in separar[1].strip().split()])

        notasSheet.write(irow, 0, idstr)
        notasSheet.write(irow, 1, nombre)

        # El estudiante no aparece. Lleno el excel de ceros, y calculo
        # la suma y la nota igual. Sigo con el siguiente.
        if llave not in todxs:
            logging.info('No se encontró respuesta de "%s"' % nombre)
            tabla.notasNull(notasSheet, sum(numPreguntas), irow, totalPts,
                            bold)
            continue

        # Localizo las respuestas del estudiante
        par: Tuple[List[str], str] = todxs.get(llave, ([], 'ausente'))
        misResp: List[str] = par[0]
        if Info.CSV_IKEY == -1:
            __comparar_usuario__(nombre, par[1], notasSheet)

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
        __calificar__(respuestas, misResp, nombre, idstr, todasResp,
                      todosPuntos, totalPts, notasSheet, irow, bold)

    notasBook.close()
    # < Para construir el archivo del reporte
    __imprimir_reporte__(carpeta, filename, todasResp, todosPuntos)
    logging.debug('Fin de evaluación.\n')
