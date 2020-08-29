"""
Tipo de pregunta, con las posibles opciones.
"""
# Pregunta de selección única
UNICA: int = 1
# Selección única, orden aleatorio.
ALEATORIO: int = 2
# Selección única, orden creciente.
CRECIENTE: int = 4
# Selección única, orden dado.
INDICES: int = 8
# Selección única, TODO Es posible eliminar la pregunta???
NINGUNA: int = 16
# Selección única, se acepta cualquier respuesta.
# Incluido cuando hay error en la respuesta.
TODAS: int = 32

# Pregunta de respuesta corta
RESP_CORTA: int = 64
# Pregunta de respuesta corta, de tipo entero
ENTERO: int = 128
# Pregunta de respuesta corta, para punto flotante.
FLOTANTE: int = 256
