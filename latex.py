from typing import List
from ppp import PPP


def get_encabezadoExamen(examen: PPP) -> str:
    """Se genera el encabezado del examen."""
    # Se comienza con el encabezado del archivo LaTeX
    texto: List[str] = [
        '\\documentclass[12pt]{article}\n\n',
        '\\usepackage[%s,%s,%s,%s]{geometry}\n' % ('scale=0.85', 'top=1in',
                                                   'papersize={8.5in,30in}',
                                                   'head=14.5pt]{geometry}'),
        '\\usepackage[utf8]{inputenc}\n',
        '\\usepackage[T1]{fontenc}\n',
        '\\usepackage[spanish]{babel}\n',
        '\\usepackage{paralist}\n',
        '\\usepackage{graphicx}\n\n',
        # Esto es para el cintillo en la parte superior
        '\\usepackage{lastpage}\n'
        '\\usepackage{fancyhdr}\n',
        '\\pagestyle{fancy}\n',
        '\\fancyhf{}\n',
        '\\lhead{Instituto Tecnol\\\'ogico de Costa Rica}\n',
        '\\rhead{P\\\'agina \\thepage~de \\pageref{LastPage}}\n',

        '\\usepackage{amsmath,amsthm,amssymb}\n',
        '\\theoremstyle{definition}\n',
        '\\newtheorem{ejer}{}\n\n',
    ]

    # Se agrega el encabezado dado por el usuario, el nombre del curso
    # al t\'itulo de la prueba, y el t\'itulo de la prueba como autor. Aqu\'i
    # acaba el encabezado, porque cada examen es a partir de ahora
    # distinto.
    texto.append(examen.encabezado)
    return ''.join(texto)


def get_inicioExamen(nombre: str, examen) -> List[str]:
    """L\'ineas previas antes de analizar cada una de las secciones.

    Recibe como argumento el nombre del estudiante para incluirlo en el
    t\'itulo.
    """
    texto = []
    txt_temp: str
    # Se agrega el nombre al examen, se comienza el documento y se
    # imprime el puntaje total.
    texto.append('\\begin{document}\n\n')
    texto.append('\\noindent \\textsc{Instituto Tecnológico de Costa Rica}')
    texto.append('\\hfill \\textsc{%s}\\\\\n' % examen.semestre)
    texto.append('\\textsc{%s} \\hfill \\textsc{Tiempo: %s}\\\\\n'
                 % (examen.cursos[0], examen.tiempo))
    for temp in examen.cursos[1:]:
        texto.append('\\textsc{%s}\\\\[1ex]\n' % temp)
    texto.append('\\textsc{%s} \\hfill \\textsc{Puntaje Total:} %d pts\\\\\n'
                 % (examen.escuelas[0], examen.get_puntaje()))
    for temp in examen.escuelas[1:]:
        texto.append('\\textsc{%s}\\bigskip\n\n' % temp)

    texto.append('\n\\begin{center}\n  {\\Large %s}\\\\[1ex]' % examen.titulo)
    texto.append('{\\large %s}\n\\end{center}\n\n' % nombre)
    return texto


def get_encabezadoInforme(numPreguntas: List[int]) -> str:
    """ Encabezado para el informe de las notas. """
    texto: List[str] = [
        '\\documentclass[12pt]{article}\n\n',
        '\\usepackage[scale=0.9,landscape]{geometry}\n',
        '\\usepackage[utf8]{inputenc}\n',
        '\\usepackage[T1]{fontenc}\n',
        '\\usepackage{nicefrac}\n',
        '\\usepackage{booktabs}\n\n',
        '\\begin{document}\n'
        '\\begin{center}\n'
        '  \\begin{tabular}{cccc'
    ]
    # El encabezado de la tabla.
    # Se va a ordenar de manera distinta:
    #   - # de carnet
    #   - nombre
    #   - nota del cuiz
    #   - n\'umero de puntos
    #   - puntaje por cada pregunta por secci\'on.
    for cada in numPreguntas:
        texto.append('|%s' % (cada * 'r'))
    texto.append('} \\\\ \\toprule \n')
    texto.append('    ID & Nombre & \\textbf{Nota} & Pts')
    for cada in numPreguntas:
        for i in range(1, cada+1):
            texto.append(' & %d' % i)
    texto.append(' \\\\ \\midrule \n')
    return ''.join(texto)
