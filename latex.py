from typing import List

def get_encabezado(examen) -> List[str]:
    """Se genera el encabezado del examen."""
    # Se comienza con el encabezado del archivo LaTeX
    texto = [
        '\\documentclass[12pt]{article}',
        '',
        '\\usepackage[scale=0.85]{geometry}',
        '\\usepackage[utf8]{inputenc}',
        '\\usepackage[T1]{fontenc}',
        '',
        '\\usepackage{amsmath,amsthm}',
        '\\theoremstyle{definition}',
    ]
    
    # Se define el estilo de la pregunta, dependiendo si hay solo una o
    # varias secciones. Si son varias secciones, entonces para cada
    # sección se tiene una enumeración nueva.
    if len(examen.secciones) > 1:
        texto.append('\\newtheorem{ejer}{}[section]')
    else:
        texto.append('\\newtheorem{ejer}{}')
    texto.append('')
    
    # Se agrega el encabezado dado por el usuario, el nombre del curso 
    # al título de la prueba, y el título de la prueba como autor. Aquí 
    # acaba el encabezado, porque cada examen es a partir de ahora 
    # distinto.
    texto += examen.encabezado
    texto.append(''.join(['\\title{', examen.curso, '}']))
    texto.append(''.join(['\\author{', examen.titulo, '}']))
    return texto


def pre_latex(nombre : str, puntaje : int) -> List[str]:
    """Líneas previas antes de analizar cada una de las secciones. 

    Recibe como argumento el nombre del estudiante para incluirlo en el 
    título.
    """
    # Se agrega el nombre al examen, se comienza el documento y se
    # imprime el puntaje total.
    latex = []
    latex.append(''.join(['\\date{', nombre, '}']))
    latex.append('')
    latex.append('\\begin{document}')
    latex.append('')
    latex.append('\\maketitle')
    latex.append('')
    latex.append(''.join(['\\noindent \\textbf{Puntaje Total :} ',
                          str(puntaje), ' pts']))
    latex.append('')
    return latex
