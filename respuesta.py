import logging
from typing import Any, List, Tuple
import math

from diccionarios import DGlobal, DFunciones
import TPreg
from fmate import descomponer
import ftexto as txt


class Respuesta:
    """ Información necesaria para evaluar las respuestas.

    Atributos
    ---------
    tipoPreg:
        Ver TPreg.py
    respuestas:
        Lista de posibles respuestas, con el porcentaje de puntuación
        respectivo.
        - Selección única: varios elementos con el índice 0-indexado de
          las respuestas correctas.
        - Respuesta corta: Una lista de tuplas de la forma
          (<resp>, <error>, <fraccion del puntaje>, <funcion>)
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

    def get_respuesta(self):
        """ Devuelve la respuesta. """
        if self.tipoPreg & TPreg.TODOS:
            return '*'
        if self.tipoPreg & TPreg.UNICA:
            return ','.join([chr(ord('A') + opcion) for opcion in self.respuestas])
        elif self.tipoPreg & TPreg.RESP_CORTA:
            return self.respuestas[0][0]

    def get_error(self) -> float:
        if not self.tipoPreg & TPreg.RESP_CORTA:
            logging.error('El error es sólo para respuesta única')
            return -1.0
        return self.respuestas[0][1]

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
            assert(opcion & (TPreg.TODOS))
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
        if self.tipoPreg & TPreg.TODOS:
            logging.debug('  Tipo -> TODOS')
            puntos = 1.0 * self.puntaje
        elif len(texto) == 0:
            puntos = 0.0
        elif self.tipoPreg & TPreg.UNICA:
            puntos = __calificar_unica__(self.respuestas, texto,
                                         self.puntaje)
        elif self.tipoPreg & TPreg.RESP_CORTA:
            puntos = __calificar_resp_corta__(self.respuestas, texto,
                                              self.puntaje)
        return (puntos, self.puntaje)

    def textoResp(self) -> str:
        """ Devuelve el texto de la respuesta correcta. """

        if self.tipoPreg & TPreg.TODOS:
            return '*'
        if self.tipoPreg & TPreg.UNICA:
            opcion = self.respuestas[0]
            return chr(ord('A') + opcion)
        elif self.tipoPreg & TPreg.RESP_CORTA:
            resp = self.respuestas[0][0]
            if isinstance(resp, float):
                cifras: int = int(math.ceil(-math.log10(self.respuestas[0][1])))
                resp = txt.decimal(resp, cifras)
            return resp
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


def __calificar_resp_corta__(respuestas, texto: str, puntaje: float) -> float:
    logging.debug('Calificar respuesta corta [%d pt]: `%s`' % (puntaje, texto))
    puntos: float = 0.0
    original = texto
    for resp, error, factor, funcion in respuestas:
        texto = original
        if funcion is not None:
            logging.debug('Funcion = `%s`', funcion)
            texto = str((eval(funcion))(texto))
            logging.debug('Nuevo texto = `%s`', texto)
        # Se pone buena si se responde. Esto aplica para *TODOS* los casos.
        if math.isinf(error):
            puntos = factor * puntaje
            break
        # Se pone para los casos particulares donde la respuesta es math.isnan.
        elif isinstance(resp, float) and math.isnan(resp):
            puntos = factor * puntaje
            break
        # Si la respuesta es un string, compara los textos.
        elif isinstance(resp, str):
            if texto.strip().lower() == resp.strip().lower():
                puntos = factor * puntaje
                break
            else:
                continue
        try:
            expr = eval(texto, DGlobal, DFunciones)
        except:
            print('\nError\n-----------')
            print('Expresión incorrecta: "%s"\n' % texto)
            logging.error('Expresión incorrecta: "%s"' % texto)
            expr = texto
        if isinstance(expr, str):
            puntos = 0.0
            break
        elif error == 0:
            logging.debug('@@@ %s (usuario) == %s (correcta)?'
                          % (str(expr), str(resp)))
            if expr == resp:
                puntos = factor * puntaje
                break
        else:
            mantisa, expo = descomponer(resp)
            menor = (mantisa - error) * 10**expo
            mayor = (mantisa + error) * 10**expo
            logging.debug('@@@ (error = %.5f) %.5f en [%.5f, %.5f]?'
                          % (error, expr, menor, mayor))
            if menor <= expr and expr <= mayor:
                puntos = factor * puntaje
                break
    return puntos
