#!/usr/bin/env python

import os
import sys
from typing import Any, Dict, List
import logging

import pregunta

logging.basicConfig(
        filename='_visualizar.log', level=logging.DEBUG, filemode='w')

encabezado: str = """
\\documentclass[12pt]{article}\n
\\usepackage[scale=0.85]{geometry}
\\usepackage[utf8]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage{paralist}
\\usepackage{graphicx}
\\usepackage{amsmath,amsthm,amssymb}
\\theoremstyle{definition}
\\newtheorem{ejer}{}\n
\\begin{document}
"""

# Si no se tienen la cantidad de argumentos correcta, se sale.
if len(sys.argv) < 3 or len(sys.argv) > 4:
    print('Se espera como argumentos el archivo .tex de la pregunta y el\n',
          'numero de muestras. De manera opcional, un archivo `.tex` para\n',
          'el encabezado, que va desde \\documentclass ... hasta \n',
          '\\begin{document}\n\n')
    sys.exit()

# Carpeta donde se va a guardar el pdf
lista: List[str] = sys.argv[1].rsplit(sep='/', maxsplit=1)
print(lista)
origen: str = lista[1]
print(origen)
output: str = '%s-vp' % origen.rsplit(sep='.', maxsplit=1)[0]
print(output)
carpeta: str = lista[0]
print(carpeta)

# Se comienza por el encabezado.
if len(sys.argv) == 4:
    finput = open(sys.argv[3], 'r')
    encabezado = '\n'.join(finput.readlines())
    finput.close()

# Se cambia al directorio del archivo.
try:
    os.chdir(carpeta)
except OSError:
    logging.critical('No se pudo abrir carpeta: `%s`' % carpeta)
    sys.exit()

# Se agrega el encabezado.
foutput = open('%s.tex' % output, 'w')
foutput.write(encabezado)

texto: str
numRep: int = int(sys.argv[2])
dParams: Dict[str, Any]
for i in range(numRep):
    dParams = {}
    foutput.write('\\begin{ejer}\n')
    texto = pregunta.get_latex(origen, dParams, True)
    foutput.write(texto)
    foutput.write('\n\\end{ejer}\n\\newpage\n\n')

foutput.write('\\end{document}\\n\\n')
foutput.close()
os.system('pdflatex %s' % output)
logging.debug('Fin de visualizar')
for file in os.listdir():
    if file.startswith(output) and not file.endswith('.pdf'):
        os.remove(file)
