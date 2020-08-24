from typing import List

def get_encabezado(examen) -> str:
    """Se genera el encabezado del examen."""
    # Se comienza con el encabezado del archivo LaTeX
    texto: List[str] = [
        '\\documentclass[12pt]{article}\n\n',
        '\\usepackage[scale=0.85,top=1in]{geometry}\n',
        '\\usepackage[utf8]{inputenc}\n',
        '\\usepackage[T1]{fontenc}\n',
        '\\usepackage{paralist}\n',
        '\\usepackage{graphicx}\n\n',
        # Esto es para el cintillo en la parte superior
        '\\usepackage{lastpage}\n'
        '\\usepackage{fancyhdr}\n',
        '\\pagestyle{fancy}\n',
        '\\fancyhf{}\n',
        '\\lhead{Tecnológico de Costa Rica}\n',
        '\\rhead{Página \\thepage~de \\pageref{LastPage}}\n',

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
    return ''.join(texto)


def pre_latex(nombre : str, examen) -> List[str]:
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
    texto.append('\\begin{document}\n\n')
    texto.append('\\noindent \\textsc{Tecnológico de Costa Rica} \hfill \\textsc{%s}\\\\\n' % examen.semestre)
    texto.append('\\textsc{%s} \hfill \\textsc{Tiempo: %s}\\\\\n' % (examen.cursos[0], examen.tiempo))
    for temp in examen.cursos[1:]:
        texto.append('\\textsc{%s}}\\\\[1ex]\n' % temp)
    texto.append('\\textsc{%s} \hfill \\textsc{Puntaje Total :} %d pts\\\\\n' % (examen.escuelas[0], examen.get_puntaje()))
    for temp in examen.escuelas[1:]:
        texto.append('\\textsc{%s}\\bigskip\n\n' % temp)

    texto.append('\n\\begin{center}\n  {\\Large %s}\\\\[1ex]' % examen.titulo)
    texto.append('{\\large %s}\n\\end{center}\n\n' % nombre)
    return texto
