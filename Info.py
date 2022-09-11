from typing import List, Tuple

"""
Claves para el texto de los archivos de entrada.

Cuando la clave puede incluir opciones, se utiliza la letra L al inicio
para aclarar que es la parte izquierda (Left) del texto.
"""
CSV_SEP: str = ';'
CSV_ICOL: int = 5
CSV_IROW: int = 1
CSV_INAME: int = 4
CSV_EMAIL: int = 3
CSV_FINAL: int = -1
# CSV_IKEY: int = CSV_FINAL    # Utiliza el # de carnet, que debe venir como última pregunta.
CSV_IKEY: int = CSV_EMAIL      # Utiliza el correo. Sirve perfecto, si *todxs* son @estudiantec.cr
# CSV_IKEY: int = CSV_INAME    # Utiliza el nombre. Puede fallar.

COMMENT: Tuple[str, str] = ('#', '%')

EXTENSION: str = '.tex'

ABRIR: str = '<'

ESCUELAS: str = '<Escuelas>'
SEMESTRE: str = '<Semestre>'
TIEMPO: str = '<Tiempo>'
CURSOS: str = '<Cursos>'
TITULO: str = '<Titulo>'
INSTRUCCIONES: str = '<Instrucciones>'
PREGUNTAS: str = '<Preguntas>'
INICIO_BLOQUE: str = '<bloque>'
FIN_BLOQUE: str = '</bloque>'
VARIABLES: str = '<variables>'
PREGUNTA: str = '<pregunta>'
RESPUESTA: str = '<respuesta>'
SOLUCION: str = '<solucion>'

# Como puede tener opciones, solamente nos
# preocupamos por el lado izquierdo.
LSECCION: str = '<Seccion'
LENCABEZADO: str = '<Encabezado'
LTIPO: str = '<tipo'
LITEM: str = '<item'

# Ver paquete paralist.
FORMATO_ITEM: str = '[A)]'

# Formato para el caso en que sea una pregunta
# por página. Ese es el formato predeterminado.
UNA_PREGUNTA_POR_PAGINA = True
LATEX_NUEVA_PREGUNTA = '\\newpage\n'
LATEX_NUEVA_PREGUNTA_BLOQUE = '\\bigskip\n'
LATEX_NUEVA_SECCION = '\\newpage\n'
PAPER_SIZE = r'papersize={8.5in,30in}'
# Si se enumera el bloque, entonces puede
# ser complicado el uso de formularios.
ENUMERAR_BLOQUE = False


# para eliminar
STRIP: str = ' <\t\n>'

# Constante que se multiplica por el número de identificación para
# generar la semilla.
BY_SHIFT: List[int] = [99929, 9929, 929, 29, 99829, 9829, 829, 89, 71, 871, 8871, 88871, 77219, 7219, 719, 19, 13, 613, 6613, 66613, 17, 617, 7517, 75617, 37, 137, 1237, 11237, 43, 443, 5443, 54443]

# Para saber si pone o no el nombre de la persona estudiante en el centro del header.
NOMBRE = False
