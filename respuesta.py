import logging

from tipo import Tipo

class Respuesta:
    """
    Clase que almacena la información necesaria para evaluar las
    respuestas.
    """
    def __init__(self, tipo):
        """
        Constructor. Recibe como argumento de entrada el tipo de 
        pregunta.
        """
        assert(tipo == Tipo.UNICA or tipo == Tipo.RESP_CORTA)
        self.tipo = tipo
        # Las respuestas son una lista abierta de cualquier tipo.
        self.respuestas = []
        # Puntaje predeterminado. Creo que es innecesario, pero por si
        # las moscas.
        self.puntaje: int = 1

    def add_opcion(self, opcion):
        """ Agrega una opcion a la pregunta. """
        # Verificamos que la opción agregada sea apropiada según el
        # tipo de pregunta.
        if self.tipo == Tipo.UNICA:
            assert(opcion & (Tipo.ALEATORIO + Tipo.CRECIENTE 
                    + Tipo.INDICES + Tipo.NINGUNA + Tipo.TODAS))
        elif self.tipo == Tipo.RESP_CORTA:
            assert(opcion & (Tipo.ENTERO + Tipo.FLOTANTE))
        else:
            assert(False)
        # Tipo se define como *intFlag*, así que las opciones se pueden
        # `sumar`. Con el operador binario `&` se puede extraer si la
        # opción está definida o no.
        self.tipo += opcion

    def add_respuesta(self, resp):
        self.respuestas.append(resp)

    def set_puntaje(self, puntaje: int):
        self.puntaje = puntaje

    def calificar(self, texto: str):
        puntos = 0
        if self.tipo & Tipo.TODAS:
            puntos = self.puntaje
        elif self.tipo & Tipo.UNICA:
            if len(self.respuestas) > 1:
                logging.error('Más de una respuesta correcta en selección única.')
            for opcion in self.respuestas:
                # Lo que hacemos es que, con que acierte una, le damos
                # los puntos de la pregunta.
                if ord(texto) - ord('A') == opcion:
                    puntos = self.puntaje
                    break
        return puntos
