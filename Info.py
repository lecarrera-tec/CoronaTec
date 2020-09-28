from typing import List
"""
Claves para el texto de los archivos de entrada.

Cuando la clave puede incluir opciones, se utiliza la letra L al inicio
para aclarar que es la parte izquierda (Left) del texto.
"""
CSV_SEP: str = ';'
CSV_ICOL: int = 5
CSV_IROW: int = 1
CSV_IKEY: int = -1

COMMENT: str = '%'
ABRIR: str = '<'
CERRAR: str = '>'

EXTENSION: str = '.tex'

ESCUELAS: str = '%sEscuelas%s' % (ABRIR, CERRAR)
SEMESTRE: str = '%sSemestre%s' % (ABRIR, CERRAR)
TIEMPO: str = '%sTiempo%s' % (ABRIR, CERRAR)
CURSOS: str = '%sCursos%s' % (ABRIR, CERRAR)
TITULO: str = '%sTitulo%s' % (ABRIR, CERRAR)
INSTRUCCIONES: str = '%sInstrucciones%s' % (ABRIR, CERRAR)
ENCABEZADO: str = '%sEncabezado%s' % (ABRIR, CERRAR)

# Como la sección puede tener opciones, solamente nos
# preocupamos por el lado izquierdo.
LSECCION: str = '%sSeccion' % ABRIR
PREGUNTAS: str = '%sPreguntas%s' % (ABRIR, CERRAR)
INICIO_BLOQUE: str = '%sbloque%s' % (ABRIR, CERRAR)
FIN_BLOQUE: str = '%s/bloque%s' % (ABRIR, CERRAR)

LTIPO: str = '%stipo' % ABRIR
VARIABLES: str = '%svariables%s' % (ABRIR, CERRAR)
PREGUNTA: str = '%spregunta%s' % (ABRIR, CERRAR)
LITEM: str = '%sitem' % ABRIR
RESPUESTA: str = '%srespuesta%s' % (ABRIR, CERRAR)
SOLUCION: str = '%ssolucion%s' % (ABRIR, CERRAR)

# Ver paquete paralist.
FORMATO_ITEM: str = '[A)]'

# para eliminar
STRIP: str = ' \t\n%s%s' % (ABRIR, CERRAR)

# Constante que se multiplica por el número de identificación para
# generar la semilla.
BY_SHIFT: List[int] = [99929, 9929, 929, 29, 99829, 9829, 829]
