"""Diccionarios separados según su funcionalidad.

Son la base de los argumentos que se pasan a la función ``eval``.
Se restringe lo máximo posible para aumentar la seguridad, y para
evitar que el usuario llame a una función aletoria en el texto de la
pregunta.

Variables
---------
DGlobal:
    Diccionario global de funciones.
DFunRandom:
    Diccionario de las funciones aleatorias que se permiten únicamente
    en la evaluación de variables.
"""

import random
import math
from typing import Any, Dict

import fdistrib
import ftexto
import fmate
import fmatriz
import fvector

DGlobal: Dict[str, Any] = {
        '__builtins__': __builtins__,
        'distrib': fdistrib,
        'math': math,
        'mate': fmate,
        'txt': ftexto,
        'matriz': fmatriz,
        'vector': fvector,
        }

DFunRandom: Dict[str, Any] = {
        'randrange': random.randrange,
        'randint': random.randint,
        'choice': random.choice,
        'sample': random.sample,
        'random': random.random,
        'uniform': random.uniform,
        'gauss': random.gauss,
}

DFunciones = {
        'inf': math.inf,
        'div': math.nan,
        'C': math.comb,
        'P': math.perm,
        'factorial': math.factorial,
        }
