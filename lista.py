#!/usr/bin/env python

import os
import random
import sys
from typing import List
import logging

from ppp import PPP
import latex
import Info


logging.basicConfig(filename='_lista.log', level=logging.DEBUG, filemode='w')

def __reemplazar__(txt: str) ->str:
    resp = txt.replace('ñ', 'n').replace('á', 'a')
    resp = resp.replace('é', 'e').replace('í', 'i')
    resp = resp.replace('ó', 'o').replace('ú', 'u')
    return resp

# Si no se tienen la cantidad de argumentos correcta, se sale.
if len(sys.argv) != 2:
    print('Se espera como argumento la lista de estudiantes')
    sys.exit()

# Vamos a guardar una lista de cada archivo .csv que existe, porque
# suponemos que cada archivo es la lista de un grupo.
lestudiantes: List[str] = []
path: str = sys.argv[1]
if path.endswith('.csv'):
    # El argumento dado no fue una carpeta, si no fue solo una lista.
    lestudiantes = [sys.argv[1]]
else:
    # Si no fue un archivo .csv, suponemos que es una carpeta.
    try:
        listdir = os.listdir(path)
    except FileNotFoundError:
        logging.critical('%s "%s" %s' % (
            'No se pudo abrir carpeta',
            sys.argv[1],
            'con las listas de estudiantes.'))
        sys.exit()
    if not path.endswith('/'):
        path = '%s/' % path
    for me in listdir:
        if me.endswith('.csv'):
            lestudiantes.append('%s%s' % (path, me))

# Directorio actual
cwd: str = os.getcwd()

# Se trabaja grupo por grupo.
carpeta: str    # Carpeta donde se guardan las listas
filename: str
lista: List[str]
linea: str    # Un estudiante de la lista.
idstr: str    # String del identificador del estudiante (# de carnet).
separar: List[str]   # Separar info del estudiante.
for path in lestudiantes:
    logging.debug('Nueva lista: %s' % path)
    # Archivo donde se guarda la lista de estudiantes.
    lista = path.rsplit(sep='/', maxsplit=1)
    carpeta = lista[0]
    filename = lista[1].rsplit(sep='.', maxsplit=1)[0]

    # Se lee el archivo de los estudiantes.
    try:
        finput = open(path, 'r')
    except FileNotFoundError:
        logging.error('No se pudo abrir lista "%s"' % path)
        continue

    # Se separa la lista por estudiante.
    Lista: List[str] = finput.readlines()
    finput.close()

    # Se comienza a generar el archivo.
    nombres: List[str] = []

    # Ahora se trabaja con cada estudiante de la Lista.
    for linea in Lista:
        # Separamos el número de identificación del resto del nombre.
        # ##-id-##, <apellidos/nombres>, xxxxx
        separar = linea.split(',')
        idstr = separar[0].strip()
        nombre = ' '.join([palabra.capitalize()
                           for palabra in separar[1].strip().split()])
        clave = '%s%s' % (nombre[:4].lower().replace(' ', '_'),
                             idstr[-6:])
        clave = __reemplazar__(clave)
        nombres.append('%s,%s\n' % (idstr,clave))

    # Se cambia de directorio.
    try:
        os.chdir('%s/' % carpeta)
    except FileNotFoundError:
        logging.critical('No se pudo cambiar a directorio.')
        sys.exit()

    # Se imprime el documento.
    fout = open('%s.txt' % filename, 'w')
    fout.writelines(nombres)
    fout.close()

    # Se devuelve a la carpeta original.
    os.chdir(cwd)
