#!/usr/bin/env python

import os
import sys
from typing import Any, Dict, List
import logging

import pregunta

logging.basicConfig(filename='_visualizar.log', level=logging.DEBUG, filemode='w')

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
    print(
    """Se espera como argumentos el archivo .tex de la pregunta y el numero de 
    muestras. De manera opcional, un archivo `.tex` para el encabezado, que va
    desde \\documentclass ... hasta \\begin{document}""")
    sys.exit()

# Carpeta donde se va a guardar el pdf
lista: List[str] = sys.argv[1].rsplit(sep='/', maxsplit=1)
filename: str = '%s-vp' % lista[1].rsplit(sep='.', maxsplit=1)[0]
carpeta: str = lista[0]


foutput = open('%s.tex' % filename, 'w')
texto: str

# Se comienza por el encabezado.
if len(sys.argv) == 4:
    finput = open(sys.argv[3], 'r')
    texto = '\n'.join(finput.readlines())
    finput.close()
    foutput.write(texto)
else:
    foutput.write(encabezado)

numRep: int = int(sys.argv[2])
dParams: Dict[str, Any]
for i in range(numRep):
    dParams = {}
    foutput.write('\\begin{ejer}\n')
    texto = pregunta.get_latex(sys.argv[1], dParams, True)
    foutput.write(texto)
    foutput.write('\n\\end{ejer}\n\\newpage\n\n')

foutput.write('\\end{document}\\n\\n')
foutput.close()
os.system('pdflatex %s' % filename)
logging.debug('Fin de visualizar')
os.replace('%s.pdf' % filename, '%s/%s.pdf' % (carpeta, filename))
for file in os.listdir():
    if file.startswith(filename):
        os.remove(file)
