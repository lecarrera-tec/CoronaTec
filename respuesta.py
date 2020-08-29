import logging
from typing import Any, List, Tuple

import TPreg

class Respuesta:
    """
    Clase que almacena la información necesaria para evaluar las
    respuestas.
    """
    def __init__(self, tipo_preg: int) -> None:
        """
        Constructor. Recibe como argumento de entrada el tipo de 
        pregunta.
        """
        assert(tipo_preg == TPreg.UNICA or tipo_preg == TPreg.RESP_CORTA)
        self.tipo_preg: int = tipo_preg
        # Las respuestas son una lista abierta de cualquier tipo.
        self.respuestas: List[Any] = []
        # Puntaje predeterminado. Creo que es innecesario, pero por si
        # las moscas.
        self.puntaje: int = 1

    def add_opcion(self, opcion: int) -> None:
        """ Agrega una opcion a la pregunta. """
        # Verificamos que la opción agregada sea apropiada según el
        # tipo de pregunta.
        if self.tipo_preg == TPreg.UNICA:
            assert(opcion & (TPreg.ALEATORIO + TPreg.CRECIENTE 
                    + TPreg.INDICES + TPreg.NINGUNA + TPreg.TODAS))
        elif self.tipo_preg == TPreg.RESP_CORTA:
            assert(opcion & (TPreg.ENTERO + TPreg.FLOTANTE))
        else:
            assert(False)
        # TPreg se define como *intFlag*, así que las opciones se pueden
        # `sumar`. Con el operador binario `&` se puede extraer si la
        # opción está definida o no.
        self.tipo_preg += opcion

    def add_respuesta(self, resp: Any) -> None:
        # TODO Definir un formato para Tuple[Any,float,float] y 
        # verificar que TResp coincida con dicho formato.
        logging.debug('Se agrega respuesta: %s' % str(resp))
        self.respuestas.append(resp)

    def set_puntaje(self, puntaje: int) -> None:
        self.puntaje = puntaje

    def calificar(self, texto: str) -> Tuple[float, int]:
        """ 
        Dependiendo del tipo de pregunta, devuelve el puntaje obtenido.
        Devuelve una tupla con el puntaje obtenido y el puntaje total de 
        la pregunta.
        """
        logging.debug('Calificar: %s' % texto)
        puntos: float = 0
        if self.tipo_preg & TPreg.TODAS:
            logging.debug('  Tipo -> TODAS')
            puntos = 1.0 * self.puntaje
        elif self.tipo_preg & TPreg.UNICA:
            logging.debug('  Tipo -> UNICA')
            if len(self.respuestas) > 1:
                logging.error('  Más de una respuesta correcta en selección única.')
            for opcion in self.respuestas:
                # Lo que hacemos es que, con que acierte una, le damos
                # los puntos de la pregunta.
                logging.debug('  Opcion: %d -- Respuesta: %d (' % (opcion, ord(texto) - ord('A')))
                if (ord(texto) - ord('A')) == opcion:
                    puntos = 1.0 * self.puntaje
                    break
        return (puntos, self.puntaje)
