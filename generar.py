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

logging.basicConfig(filename='output.log', level=logging.DEBUG, filemode='w')

# Si no se tienen la cantidad de argumentos correcta, se sale.
if (len(sys.argv) != 3):
    print("Se espera como argumentos el archivo ppp y el archivo de los"
            + "estudiantes.")
    sys.exit()

# Se lee el archivo de la estructura general del examen
# y se genera (casi todo) el encabezado.
examen = PPP(sys.argv[1])
encabezado: List[str] = latex.get_encabezado(examen)

# Se lee el archivo de los estudiantes, y se guarda la Lista.
finput = open(sys.argv[2], 'r')
Lista: List[str] = finput.readlines()
finput.close()

# Ahora se trabaja con cada estudiante de la Lista.
linea : str    # L\'inea de c\'odigo
idstr : str    # String del identificador del estudiante.
separar : List[str]   # Separar CSV
for linea in Lista:
    logging.info('Nuevo examen.')
    # Separamos el número de identificación del resto del nombre.
    # ##-id-## <apellidos/nombres>
    separar = linea.split(',')
    idstr = separar[0].strip()
    nombre = separar[1].strip()

    # Se inicializa la semilla usando el identificador multiplicado por
    # una constante diab\'olica.
    random.seed(info.BY_SHIFT * int(idstr))

    # Se comienza a generar el archivo.
    tex = latex.pre_latex(nombre, examen.get_puntaje())
    tex.append('\\noindent \\textbf{Instrucciones: }')
    tex.append(examen.instrucciones)

    # Si es s\'olo una secci\'on y no tiene t\'itulo, entonces no agregamos
    # la etiqueta de secci\'on en LaTeX. En caso contrario, se agrega
    # la etiqueta para cada una de las secciones, aunque no tengan 
    # t\'itulo.
    seccion = examen.secciones[0]
    logging.info('Se tienen %d secciones en total' % len(examen.secciones))
    if len(examen.secciones) > 1 or len(seccion.titulo) > 0:
        tex.append('  \\section{%s}\n\n' % seccion.titulo)
        tex += seccion.get_latex()

    # Ahora se trabaja con el resto de las secciones
    for seccion in examen.secciones[1:]:
        tex.append('  \\section{%s}\n\n' % seccion.titulo)
        tex += seccion.get_latex()

    # Cerrando el documento.
    tex.append('\\end{document}\n')

    # Se imprime el documento.
    filename = idstr[-6:] + '.tex'
    fout = open(filename, 'w')
    fout.writelines(encabezado)
    fout.writelines(tex)
    fout.close();

    # Se genera el pdf
    os.system('pdflatex %s' % filename)
    os.system('pdflatex %s' % filename)
    logging.info('Fin de examen\n')
