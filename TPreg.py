"""
Tipo de pregunta, con las posibles opciones.
"""
# Pregunta de selecci\'on \'unica
UNICA: int = 1
# Selecci\'on \'unica, orden aleatorio.
ALEATORIO: int = 2
# Selecci\'on \'unica, orden creciente.
CRECIENTE: int = 4
# Selecci\'on \'unica, orden dado.
INDICES: int = 8
# Selecci\'on \'unica, TODO Es posible eliminar la pregunta???
NINGUNA: int = 16
# Selecci\'on \'unica, se acepta cualquier respuesta.
# Incluido cuando hay error en la respuesta.
TODAS: int = 32

# Pregunta de respuesta corta
RESP_CORTA: int = 64
# Pregunta de respuesta corta, de tipo entero
ENTERO: int = 128
# Pregunta de respuesta corta, para punto flotante.
FLOTANTE: int = 256
