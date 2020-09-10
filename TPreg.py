""" Tipo de pregunta, con las posibles opciones.  """

# Pregunta de selecci\'on \'unica
UNICA: int = 1
# Selecci\'on \'unica, orden aleatorio.
ALEATORIO: int = 2
# Selecci\'on \'unica, orden creciente.
CRECIENTE: int = 4
# Selecci\'on \'unica, orden dado.
INDICES: int = 8
# Selecci\'on \'unica, se acepta cualquier respuesta.
# Incluido cuando hay error en la respuesta.
TODOS: int = 16

# Pregunta de respuesta corta
RESP_CORTA: int = 64
# Pregunta de respuesta corta, de tipo entero
ENTERO: int = 128
# Pregunta de respuesta corta, para punto flotante.
FLOTANTE: int = 256

# Tipo de encabezado
ENCABEZADO: int = 512

# Tipo de pregunta desconocida
NINGUNA: int = 1024
