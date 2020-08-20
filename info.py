"""
Opciones para el texto de los archivos de entrada.
"""
COMMENT: str = '#'
ABRIR: str = '<'
CERRAR: str = '>'

EXTENSION: str = '.tex'

CURSO: str = '%sCurso%s' % (ABRIR, CERRAR)
TITULO: str = '%sTitulo%s' % (ABRIR, CERRAR)
INSTRUCCIONES: str = '%sInstrucciones%s' % (ABRIR, CERRAR)
ENCABEZADO: str = '%sEncabezado%s' % (ABRIR, CERRAR)

# Como la sección puede tener opciones, solamente nos 
# preocupamos por el lado izquierdo.
LSECCION: str = '%sSeccion' % ABRIR
PREGUNTAS: str = '%sPreguntas%s' % (ABRIR, CERRAR)

LTIPO: str = '%stipo' % ABRIR
VARIABLES: str = '%svariables%s' % (ABRIR, CERRAR)
PREGUNTA: str = '%spregunta%s' % (ABRIR, CERRAR)
ITEM: str = '%sitem%s' % (ABRIR, CERRAR)
RESPUESTA: str = '%srespuesta%s' % (ABRIR, CERRAR)
SOLUCION: str = '%ssolucion%s' % (ABRIR, CERRAR)

# Constante que se multiplica por el número de identificación
# para generar la semilla.
BY_SHIFT: int = 99913
