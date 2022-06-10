from typing import List, Tuple

UNA_PREGUNTA_POR_PAGINA = False
# Si se enumera el bloque, entonces puede
# ser complicado el uso de formularios.
ENUMERAR_BLOQUE = False

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
ENCABEZADO: str = '<Encabezado>'

# Como la sección puede tener opciones, solamente nos
# preocupamos por el lado izquierdo.
LSECCION: str = '<Seccion'
PREGUNTAS: str = '<Preguntas>'
INICIO_BLOQUE: str = '<bloque>'
FIN_BLOQUE: str = '</bloque>'

LTIPO: str = '<tipo'
VARIABLES: str = '<variables>'
PREGUNTA: str = '<pregunta>'
LITEM: str = '<item'
RESPUESTA: str = '<respuesta>'
SOLUCION: str = '<solucion>'

# Ver paquete paralist.
FORMATO_ITEM: str = '[A)]'

# Formato para el documento
if UNA_PREGUNTA_POR_PAGINA:
    LATEX_NUEVA_PREGUNTA = '\\newpage'
    LATEX_NUEVA_SECCION = '\\newpage'
    PAPER_SIZE = 'papersize={8.5in,30in}'
else:
    LATEX_NUEVA_PREGUNTA = ''
    LATEX_NUEVA_SECCION = ''
    PAPER_SIZE = 'papersize={8.5in,11in}'

# para eliminar
STRIP: str = ' <\t\n>'

# Constante que se multiplica por el número de identificación para
# generar la semilla.
BY_SHIFT: List[int] = [99929, 9929, 929, 29, 99829, 9829, 829]
