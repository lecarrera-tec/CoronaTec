"""
Claves para el texto de los archivos de entrada.

Cuando la clave puede incluir opciones, se utiliza la letra L al inicio
para aclarar que es la parte izquierda (Left) del texto.
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
LITEM: str = '%sitem' % ABRIR
RESPUESTA: str = '%srespuesta%s' % (ABRIR, CERRAR)
SOLUCION: str = '%ssolucion%s' % (ABRIR, CERRAR)

# Ver paquete paralist.
FORMATO_ITEM: str = '[A)]'

# para eliminar
STRIP = ' \t\n%s%s' % (ABRIR, CERRAR)

# Constante diabólica que se multiplica por el número de identificación
# para generar la semilla.
BY_SHIFT: int = 99929
