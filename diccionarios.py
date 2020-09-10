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
        'sample': random.sample,
        'random': random.random,
        'uniform': random.uniform,
        'gauss': random.gauss,
}

DFunciones: Dict[str, Any] = {
        # Funciones generales
        'range': range,
        'len'  : len,

        # Funciones de matematica
        'round'     : round,
        'pow'       : pow,
        'abs'       : abs,
        'sum'       : sum,
        'acos'      : math.acos,
        'acosh'     : math.acosh,
        'asin'      : math.asin,
        'asinh'     : math.asinh,
        'atan'      : math.atan,
        'atan2'     : math.atan2,
        'atanh'     : math.atanh,
        'ceil'      : math.ceil,
        'comb'      : math.comb,
        'cos'       : math.cos,
        'cosh'      : math.cosh,
        'degrees'   : math.degrees,
        'dist'      : math.dist,
        'erf'       : math.erf,
        'erfc'      : math.erfc,
        'exp'       : math.exp,
        'factorial' : math.factorial,
        'floor'     : math.floor,
        'fmod'      : math.fmod,
        'gamma'     : math.gamma,
        'gcd'       : math.gcd,
        'hypot'     : math.hypot,
        'inf'       : math.inf,
        'isqrt'     : math.isqrt,
        'log'       : math.log,
        'log10'     : math.log10,
        'modf'      : math.modf,
        'perm'      : math.perm,
        'pi'        : math.pi,
        'prod'      : math.prod,
        'radians'   : math.radians,
        'sin'       : math.sin,
        'sinh'      : math.sinh,
        'sqrt'      : math.sqrt,
        'tan'       : math.tan,
        'tanh'      : math.tanh,
        'trunc'     : math.trunc,

        'factores' : fmate.factores,

        # Funciones de texto
        'txtFrac': ftexto.txtFraccion,
        'txtRaiz': ftexto.txtRaiz,
        'txtCoef': ftexto.txtCoef,
        'txtExpo': ftexto.txtExpo,
        'txtConSigno': ftexto.txtConSigno,
}
