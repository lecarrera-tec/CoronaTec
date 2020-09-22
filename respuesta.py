import logging
from typing import Any, List, Tuple
from math import ceil, log10

from diccionarios import DGlobal, DFunciones
import TPreg
from fmate import mantisa
from ftexto import txtFloat


class Respuesta:
    """ Información necesaria para evaluar las respuestas.

    Atributos
    ---------
    tipoPreg:
        Ver TPreg.py
    respuestas:
        Lista de posibles respuestas, con el porcentaje de puntuaci\'on
        respectivo.
        - Selecci\'on \'unica: un sólo elemento con el \'indice 0-indexado
          de la respuesta correcta.
        - Respuesta corta entera: un sólo elemento con la respuesta
          correcta.
        - Respuesta corta flotante: Una lista de tuplas de la forma
          (<resp>, <error>, <fraccion del puntaje>)
    puntaje:
        Puntaje de la pregunta.
    """

    def __init__(self, tipoPreg: int) -> None:
        """ Constructor.

        Argumentos
        ----------
        tipoPreg:
            Tipo de pregunta de la respuesta.
        """

        assert(tipoPreg == TPreg.UNICA or tipoPreg == TPreg.RESP_CORTA
               or tipoPreg == TPreg.ENCABEZADO)
        self.tipoPreg: int = tipoPreg
        # Las respuestas son una lista abierta de cualquier tipo.
        self.respuestas: List[Any] = []
        # Puntaje predeterminado. Creo que es innecesario, pero por si
        # las moscas.
        self.puntaje: int = 1

    def add_opcion(self, opcion: int) -> None:
        """ Agrega una opcion a la pregunta.

        Argumentos
        ----------
        opcion:
            ver TPreg.py
        """

        # Verificamos que la opción agregada sea apropiada según el
        # tipo de pregunta.
        if self.tipoPreg & TPreg.UNICA:
            assert(opcion & (TPreg.ALEATORIO + TPreg.CRECIENTE
                             + TPreg.INDICES + TPreg.TODOS))
        elif self.tipoPreg & TPreg.RESP_CORTA:
            assert(opcion & (TPreg.ENTERO + TPreg.FLOTANTE))
        else:
            assert(False)
        # TPreg se define como *intFlag*, así que las opciones se pueden
        # `sumar`. Con el operador binario `&` se puede extraer si la
        # opción está definida o no.
        self.tipoPreg += opcion

    def add_respuesta(self, resp: Any) -> None:
        logging.debug('Se agrega respuesta: %s' % str(resp))
        self.respuestas.append(resp)

    def set_puntaje(self, puntaje: int) -> None:
        self.puntaje = puntaje

    def calificar(self, texto: str) -> Tuple[float, int]:
        """ Califica una pregunta.

        Argumentos
        ----------
        texto:
            Respuesta del estudiante.
        Devuelve
        --------
        Una tupla con el puntaje obtenido y el puntaje total de la
        pregunta.
        """
        logging.debug('Calificar: %s' % texto)
        puntos: float = 0
        if len(texto) == 0:
            puntos = 0.0
        elif self.tipoPreg & TPreg.TODOS:
            logging.debug('  Tipo -> TODOS')
            puntos = 1.0 * self.puntaje
        elif self.tipoPreg & TPreg.UNICA:
            puntos = __calificar_unica__(self.respuestas, texto,
                                         self.puntaje)
        elif self.tipoPreg & TPreg.ENTERO:
            assert(self.tipoPreg & TPreg.RESP_CORTA)
            puntos = __calificar_entero__(self.respuestas, texto,
                                          self.puntaje)
        elif self.tipoPreg & TPreg.FLOTANTE:
            assert(self.tipoPreg & TPreg.RESP_CORTA)
            puntos = __calificar_flotante__(self.respuestas, texto,
                                            self.puntaje)
        return (puntos, self.puntaje)

    def textoResp(self) -> str:
        """ Devuelve el texto de la respuesta correcta. """

        if self.tipoPreg & TPreg.UNICA:
            if self.tipoPreg & TPreg.TODOS:
                return '*'
            opcion = self.respuestas[0]
            return chr(ord('A') + opcion)
        elif self.tipoPreg & TPreg.RESP_CORTA:
            if self.tipoPreg & TPreg.ENTERO:
                return str(self.respuestas[0])
            elif self.tipoPreg & TPreg.FLOTANTE:
                cifras: int = int(ceil(-log10(self.respuestas[0][1])))
                return txtFloat(self.respuestas[0][0], cifras)
        logging.error('No se pudo determinar el tipo de pregunta')
        return ''


def __calificar_unica__(respuestas, texto: str, puntaje: int) -> float:
    logging.debug('  Tipo -> UNICA')
    puntos: float = 0
    for opcion in respuestas:
        # Lo que hacemos es que, con que acierte una, le damos
        # los puntos de la pregunta.
        logging.debug(
                'Opcion: %d -- Respuesta: %d' % (
                    opcion,
                    -1 if len(texto) == 0 else ord(texto) - ord('A')))
        if len(texto) > 0 and ((ord(texto) - ord('A')) == opcion):
            puntos = 1.0 * puntaje
            break
    return puntos


def __calificar_entero__(respuestas, texto: str, puntaje: int) -> float:
    expr = eval(texto, DGlobal, DFunciones)
    puntos: float = 0.0
    for resp in respuestas:
        if expr == resp:
            puntos = 1.0 * puntaje
            break
    return puntos


def __calificar_flotante__(respuestas, texto: str, puntaje: int) -> float:
    expr = eval(texto, DGlobal, DFunciones)
    puntos: float = 0.0
    for resp in respuestas:
        assert(resp[1] >= 0)
        base10 = mantisa(resp[0])
        menor = (base10[0] - resp[1]) * pow(10, base10[1])
        mayor = (base10[0] + resp[1]) * pow(10, base10[1])
        if menor <= expr and expr <= mayor:
            puntos = resp[2] * puntaje
            break
    return puntos
