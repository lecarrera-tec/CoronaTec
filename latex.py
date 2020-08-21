from typing import List

def get_encabezado(examen) -> List[str]:
    """Se genera el encabezado del examen."""
    # Se comienza con el encabezado del archivo LaTeX
    texto: List[str] = [
        '\\documentclass[12pt]{article}\n\n',
        '\\usepackage[scale=0.85]{geometry}\n',
        '\\usepackage[utf8]{inputenc}\n',
        '\\usepackage[T1]{fontenc}\n',
        '\\usepackage{paralist}\n',
        '\\usepackage{graphicx}\n',
        '\\usepackage{amsmath,amsthm,amssymb}\n',
        '\\theoremstyle{definition}\n',
    ]
    
    # Se define el estilo de la pregunta, dependiendo si hay solo una o
    # varias secciones. Si son varias secciones, entonces para cada
    # sección se tiene una enumeración nueva.
    if len(examen.secciones) > 1:
        texto.append('\\newtheorem{ejer}{}[section]\n\n')
    else:
        texto.append('\\newtheorem{ejer}{}\n\n')
    
    # Se agrega el encabezado dado por el usuario, el nombre del curso 
    # al título de la prueba, y el título de la prueba como autor. Aquí 
    # acaba el encabezado, porque cada examen es a partir de ahora 
    # distinto.
    texto.append(examen.encabezado)
    texto.append('\\title{%s}\n' % examen.curso)
    texto.append('\\author{%s}\n' % examen.titulo)
    return texto


def pre_latex(nombre : str, puntaje : int) -> List[str]:
    """Líneas previas antes de analizar cada una de las secciones. 

    Recibe como argumento el nombre del estudiante para incluirlo en el 
    título.
    """
    # Vamos a capitalizar el nombre, es decir, la primera letra en
    # mayúscula y el resto en minúscula.
    texto: List[str] = nombre.split()
    lista: List[str] = []
    for palabra in texto:
        lista.append(palabra.capitalize())
    nombre = ' '.join(lista)

    texto = []
    # Se agrega el nombre al examen, se comienza el documento y se
    # imprime el puntaje total.
    texto.append('\\date{%s}\n\n' % nombre)
    texto.append('\\begin{document}\n\n')
    texto.append('\\maketitle\n\n')
    texto.append('\\noindent \\textbf{Puntaje Total :} %d pts\n\n' % puntaje)
    return texto
