#!/usr/bin/env python

import os
import random
import sys
from typing import List
import logging

from ppp import PPP
import latex
import Info


def __primera_seccion__(tex, examen, seccion):
    if len(examen.secciones) > 1 or len(seccion.titulo) > 0:
        tex.append('  \\newpage\n')
        tex.append('  \\section{%s %s %d puntos)}}\n\n'
                   % (seccion.titulo,
                      '{\\normalsize (total de la secci\\\'on:',
                      seccion.get_puntaje()))
    else:
        # Solamente se tiene una sección sin titulo.
        tex.append('  \\newpage\n')
    tex.append(seccion.get_latex())


def __resto_secciones__(tex, examen, seccion):
    for seccion in examen.secciones[1:]:
        tex.append('\\newpage\n')
        tex.append('\\section{%s %s %d puntos)}}\n\n'
                   % (seccion.titulo,
                      '{\\normalsize (total de la secci\\\'on:',
                      seccion.get_puntaje()))
        tex.append(seccion.get_latex())
    # Cerrando el documento.
    tex.append('\\end{document}\n')

def __reemplazar__(txt: str) ->str:
    resp = txt.replace('ñ', 'n').replace('á', 'a')
    resp = resp.replace('é', 'e').replace('í', 'i')
    resp = resp.replace('ó', 'o').replace('ú', 'u')
    return resp

logging.basicConfig(filename='_generar.log', level=logging.DEBUG, filemode='w')

# Si no se tienen la cantidad de argumentos correcta, se sale.
if len(sys.argv) < 3 or len(sys.argv) > 4:
    print('%s%s%s' % (
            'Se espera como argumentos el archivo ppp y la carpeta con las ',
            'listas de los estudiantes.,\n y de manera opcional el índice',
            'de repetición del examen'))
    sys.exit()

# Índice de repetición del examen. Por default es 0.
indRepeticion: int = 0
if len(sys.argv) == 4:
    indRepeticion = int(sys.argv[3])
    assert(indRepeticion < len(Info.BY_SHIFT))

# Se lee el archivo de la estructura general del examen
# y se genera (casi todo) el encabezado.
examen = PPP(sys.argv[1])
encabezado: str = latex.get_encabezadoExamen(examen)

# Vamos a guardar una lista de cada archivo .csv que existe, porque
# suponemos que cada archivo es la lista de un grupo.
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
    path = os.path.join(path, '')
    for me in listdir:
        if me.endswith('.csv'):
            lestudiantes.append('%s%s' % (path, me))

# Directorio actual
cwd: str = os.getcwd()

# Se trabaja grupo por grupo.
carpeta: str    # Carpeta donde se guardan los pdf's.
filename: str
lista: List[str]
linea: str    # Un estudiante de la lista.
idstr: str    # String del identificador del estudiante (# de carnet).
separar: List[str]   # Separar info del estudiante.
for path in lestudiantes:
    logging.debug('Nueva lista: %s' % path)
    # Carpeta donde se van a guardar los pdf's de los exámenes.
    lista = os.path.split(path)
    filename = lista[1].rsplit(sep='.', maxsplit=1)[0]
    nombre = os.path.basename(sys.argv[1][:-4]).upper()
    carpeta = os.path.join(lista[0], '%s-%s' % (nombre, filename.upper()))
    if not os.path.exists(carpeta):
        os.mkdir(carpeta)

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
    for linea in Lista:
        logging.debug('Nuevo examen: %s' % linea)
        # Separamos el número de identificación del resto del nombre.
        # ##-id-##, <apellidos/nombres>, xxxxx
        separar = linea.split(',')
        idstr = separar[0].strip()
        nombre = ' '.join([palabra.capitalize()
                           for palabra in separar[1].strip().split()])

        # Se inicializa la semilla usando el identificador multiplicado
        # por una constante, según el índice de repetición dado.
        seed = Info.BY_SHIFT[indRepeticion] * int(idstr)
        logging.debug('numero de carnet: %s' % idstr)
        logging.debug('Random: seed = %d' % seed)
        random.seed(seed)

        # Se comienza a generar el archivo.
        tex: List[str] = latex.get_inicioExamen(nombre, examen)
        tex.append('\\noindent\\rule{\\textwidth}{1pt}\\\\[1ex]\n')
        tex.append('\\noindent \\textbf{Instrucciones: }')
        tex.append('%s\n\n\\noindent\\rule{\\textwidth}{1pt}\n\n'
                   % examen.instrucciones)

        # Si es sólo una sección y no tiene título, entonces no agregamos
        # la etiqueta de sección en LaTeX. En caso contrario, se agrega
        # la etiqueta para cada una de las secciones, aunque no tengan
        # título.
        seccion = examen.secciones[0]
        logging.debug('Se tienen %d secciones' % len(examen.secciones))
        __primera_seccion__(tex, examen, seccion)

        # Ahora se trabaja con el resto de las secciones
        __resto_secciones__(tex, examen, seccion)

        # Se cambia de directorio.
        try:
            os.chdir(os.path.join(carpeta, ''))
        except FileNotFoundError:
            logging.critical('No se pudo cambiar a directorio.')
            sys.exit()

        # Se imprime el documento.
        # Se cambia el identificador.
        # idx = 1 + nombre.find(' ')
        # filename = '%s%s' % (idstr[-6:],
        #                      nombre[idx:idx+4].lower().replace(' ', '_'))
        filename = '%s%s' % (nombre[:4].lower().replace(' ', '_'),
                             idstr[-6:])
        filename = __reemplazar__(filename)
        fout = open('%s.tex' % filename, 'w')
        fout.write(encabezado)
        fout.writelines(tex)
        fout.close()

        # Se genera el pdf.
        os.system('pdflatex %s' % filename)
        os.system('pdflatex %s' % filename)
        os.system('pdfcrop -margins 20 %s.pdf temp.pdf' % filename)

        # Se eliminan los archivo '*.{aux,log,tex,...}'
        flist = [f for f in os.listdir() if f.startswith(filename)]
        for f in flist:
            os.remove(f)

        os.rename('temp.pdf', '%s.pdf' % filename)
        logging.debug('Fin de examen\n')

        # Se devuelve a la carpeta original.
        os.chdir(cwd)
