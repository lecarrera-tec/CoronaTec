from typing import List, Tuple
"""
Claves para el texto de los archivos de entrada.

Cuando la clave puede incluir opciones, se utiliza la letra L al inicio
para aclarar que es la parte izquierda (Left) del texto.
"""
CSV_SEP: str = ';'
CSV_ICOL: int = 5
CSV_IROW: int = 1
# CSV_IKEY: int = -1
CSV_IKEY: int = 4
CSV_INAME: int = 4
CSV_EMAIL: int = 3

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

# para eliminar
STRIP: str = ' <\t\n>'

# Constante que se multiplica por el número de identificación para
# generar la semilla.
BY_SHIFT: List[int] = [99929, 9929, 929, 29, 99829, 9829, 829]
