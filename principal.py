#!/usr/bin/env python

from ppp import ppp
from section import section
import sys
import random
import latex
# Vamos a importar las funciones a las cuales tienen acceso los
# usuarios, 
from random import randrange, randint, choice, uniform, gauss, 


# Se lee el archivo de la estructura general del examen
# y se genera (casi todo) el encabezado.
examen = ppp(sys.argv[1])
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
    random.seed(info.by_shift * int(idstr))

    # Se comienza a generar el archivo.
    latex = examen.pre_latex(nombre, examen.get_puntaje())

    # Analizamos el caso donde es s\'olo una secci\'on
    seccion = examen.secciones[0]
    if len(examen.secciones) > 1 or len(seccion.title) > 0:
        latex.append('  \\section{' + seccion.title + '}')
        latex.append('')
        latex += seccion.latex()

    # Ahora se trabaja con el resto de las secciones
    for seccion in examen.secciones[1:]:
        latex.append('  \\section{' + seccion.title + '}')
        latex.append('')
        latex += seccion.latex()

    # Cerrando el documento.
    latex.append('\\end{document}')

    # Se imprime el documento.
    filename = idstr[-6:] + '.tex'
    fout = open(filename, 'w')
    fout.writelines(encabezado)
    fout.writelines(latex)

