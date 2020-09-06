from typing import List

import xlsxwriter

def encabezadoNotas(notas, numPregs: int) -> None:
    notas.set_column('A:A', 10)
    notas.set_column('B:B', 40)
    notas.write(0,0,'# de carnet');
    notas.write(0,1,'Nombre');
    notas.write(0,2,'Nota');
    notas.write(0,3,'Puntaje');
    # Las primeras 4 columnas est\'an ocupadas.
    for i in range(numPregs):
        notas.write(0, i + 4, 'Preg. %d' % (i + 1))

def notasNull(notas, numPregs: int, irow: int) -> None:
    # Las primeras 4 columnas est\'an ocupadas.
    for i in range(numPregs):
        notas.write(irow, i + 4, 0)
