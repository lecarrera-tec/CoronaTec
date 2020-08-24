#!/usr/bin/env python

import os
import random
import sys
from typing import List
import logging

from ppp import PPP
from seccion import Seccion
import latex
import info

logging.basicConfig(filename='output.log', level=logging.INFO, filemode='w')

# Si no se tienen la cantidad de argumentos correcta, se sale.
if len(sys.argv) < 3 or len(sys.argv) > 4:
    print('%s%s%s' % (
            'Se espera como argumentos el archivo ppp y la carpeta con las ',
            'listas de los estudiantes.,\n y de manera opcional el índice',
            'de repetición del examen'))
    sys.exit()

# Índice de repetición del examen. Por default es 0.
ind_repeticion: int = 0
if len(sys.argv) == 4:
    ind_repeticion = int(sys.argv[3])
    assert(ind_repeticion < len(info.BY_SHIFT))

# Se lee el archivo de la estructura general del examen
# y se genera (casi todo) el encabezado.
examen = PPP(sys.argv[1])
encabezado: str = latex.get_encabezado(examen)

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

# Se trabaja grupo por grupo.
carpeta: str    # Carpeta donde se guardan los pdf's.
filename: str 
lista: List[str]
linea : str    # Un estudiante de la lista.
idstr : str    # String del identificador del estudiante (# de carnet).
separar : List[str]   # Separar info del estudiante.
for path in lestudiantes:
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

    # Se guarda la lista de cada estudiante.
    Lista: List[str] = finput.readlines()
    finput.close()
    
    # Ahora se trabaja con cada estudiante de la Lista.
    for linea in Lista:
        logging.debug('Nuevo examen.')
        # Separamos el número de identificación del resto del nombre.
        # ##-id-##, <apellidos/nombres>, xxxxx
        separar = linea.split(',')
        idstr = separar[0].strip()
        nombre = separar[1].strip()
    
        # Se inicializa la semilla usando el identificador multiplicado por
        # una constante.
        random.seed(info.BY_SHIFT[ind_repeticion] * int(idstr))
    
        # Se comienza a generar el archivo.
        tex: List[str] = latex.pre_latex(nombre, examen)
        tex.append('\\noindent\\rule{\\textwidth}{1pt}\\\\[1ex]\n')
        tex.append('\\noindent \\textbf{Instrucciones: }')
        tex.append('%s\\\\\\rule{\\textwidth}{1pt}\n\n' % examen.instrucciones)
    
        # Si es sólo una sección y no tiene título, entonces no agregamos
        # la etiqueta de sección en LaTeX. En caso contrario, se agrega
        # la etiqueta para cada una de las secciones, aunque no tengan 
        # título.
        seccion = examen.secciones[0]
        logging.debug('Se tienen %d secciones en total' % len(examen.secciones))
        if len(examen.secciones) > 1 or len(seccion.titulo) > 0:
            tex.append('  \\section{%s}\n\n' % seccion.titulo)
            tex.append(seccion.get_latex())
    
        # Ahora se trabaja con el resto de las secciones
        for seccion in examen.secciones[1:]:
            tex.append('  \\section{%s}\n\n' % seccion.titulo)
            tex.append(seccion.get_latex())
    
        # Cerrando el documento.
        tex.append('\\end{document}\n')
    
        # Se imprime el documento.
        filename = idstr[-6:]
        fout = open('%s.tex' % filename, 'w')
        fout.write(encabezado)
        fout.writelines(tex)
        fout.close();
    
        # Se genera el pdf.
        os.system('pdflatex %s' % filename)
        os.system('pdflatex %s' % filename)
        logging.debug('Fin de examen\n')

        # Se mueve el pdf a la carpeta respectiva, y se eliminan el 
        # resto de los archivos.
        os.replace('%s.pdf' % filename, '%s/%s.pdf' % (carpeta, filename))
        lista = os.listdir('./')
        for fname in lista:
            if fname.startswith(filename):
                os.remove(fname)
