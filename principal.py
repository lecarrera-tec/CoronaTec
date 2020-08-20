#!/usr/bin/env python

import sys
import random

from ppp import PPP
from seccion import Seccion
import latex
import info

# Se lee el archivo de la estructura general del examen
# y se genera (casi todo) el encabezado.
examen = PPP(sys.argv[1])
encabezado = latex.get_encabezado(examen)

# Se lee el archivo de los estudiantes, y se guarda la Lista.
finput = open(sys.argv[2], 'r')
Lista = finput.readlines()
finput.close()

# Ahora se trabaja con cada estudiante de la Lista.
for linea in Lista:
    # Separamos el n\'umero de identificaci\'on del resto del nombre.
    # ##-id-## <apellidos/nombres>
    idx = linea.find(' ')
    idstr = linea[0:idx].strip()
    nombre = linea[idx:].strip()

    # Se inicializa la semilla usando el 
    random.seed(info.BY_SHIFT * int(idstr))

    # Se comienza a generar el archivo.
    tex = latex.pre_latex(nombre, examen.get_puntaje())

    # Analizamos el caso donde es s\'olo una secci\'on
    seccion = examen.secciones[0]
    if len(examen.secciones) > 1 or len(seccion.titulo) > 0:
        tex.append('  \\section{' + seccion.titulo + '}')
        tex.append('')
        tex += seccion.get_latex()

    # Ahora se trabaja con el resto de las secciones
    for seccion in examen.secciones[1:]:
        tex.append('  \\section{' + seccion.titulo + '}')
        tex.append('')
        tex += seccion.get_latex()

    # Cerrando el documento.
    tex.append('\\end{document}')

    # Se imprime el documento.
    filename = idstr[-6:] + '.tex'
    fout = open(filename, 'w')
    fout.writelines(encabezado)
    fout.writelines(tex)

