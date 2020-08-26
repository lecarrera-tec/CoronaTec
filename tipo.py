from enum import IntFlag, auto
class Tipo(IntFlag):
    """
    Tipo de pregunta, con las posibles opciones.
    """
    # Pregunta de selección única
    UNICA = auto()
    # Selección única, orden aleatorio.
    ALEATORIO = auto()
    # Selección única, orden creciente.
    CRECIENTE = auto()
    # Selección única, orden dado.
    INDICES = auto()
    # Selección única, TODO Es posible eliminar la pregunta???
    NINGUNA = auto()
    # Selección única, se acepta cualquier respuesta.
    # Incluido cuando hay error en la respuesta.
    TODAS = auto()

    # Pregunta de respuesta corta
    RESP_CORTA = auto()
    # Pregunta de respuesta corta, de tipo entero
    ENTERO = auto()
    # Pregunta de respuesta corta, para punto flotante.
    FLOTANTE = auto()
