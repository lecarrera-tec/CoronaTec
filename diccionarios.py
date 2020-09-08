"""Diccionarios separados según su funcionalidad.

Son la base de los argumentos que se pasan a la función ``eval``.
Se restringe lo máximo posible para aumentar la seguridad, y para
evitar que el usuario llame a una función aletoria en el texto de la
pregunta.

Variables
---------
DGlobal:
    Diccionario vacío que se va a pasar como diccionario global.
DFunRandom:
    Diccionario de las funciones aleatorias que se permiten únicamente
    en la evaluación de variables.
DFunciones:
    Diccionario de funciones que son accesibles tanto en la definición
    de variables como en la generación de la pregunta e items.
"""

import random
import math
from typing import Any, Dict

import ftexto
import fmate

DGlobal: Dict[str, Any] = {'__builtins__' : None}

DFunRandom: Dict[str, Any] = {
        'randrange': random.randrange,
        'randint': random.randint,
        'choice': random.choice,
        'shuffle': random.shuffle,
        'sample': random.sample,
        'random': random.random,
        'uniform': random.uniform,
        'gauss': random.gauss,
}

DFunciones: Dict[str, Any] = {
        # Funciones generales
        'range': range,

        # Funciones de matematica
        'round': round,
        'pow' : pow,
        'abs' : abs,

        'binomial': math.comb,
        'factorial': math.factorial,
        'gcd': math.gcd,
        'sqrt': math.sqrt,

        'factores': fmate.factores,

        # Funciones de texto
        'txtFrac': ftexto.txtFraccion,
        'txtRaiz': ftexto.txtRaiz,
        'txtCoef': ftexto.txtCoef,
        'txtExpo': ftexto.txtExpo,
}
