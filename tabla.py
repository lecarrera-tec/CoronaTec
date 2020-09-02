from typing import List

import xlsxwriter

def encabezadoNotas(notas, numPreg: List[int]) -> None:
    notas.set_column('A:A', 10)
    notas.set_column('B:B', 40)
    notas.write(0,0,'# de carnet');
    notas.write(0,1,'Nombre');
    notas.write(0,2,'Nota');
    notas.write(0,3,'Puntaje');
    cont = 0
    icol = 3
    for n in numPreg:
        cont += 1
        for i in range(1,n+1):
            icol += 1
            notas.write(0, icol, 'Preg. %d.%d' % (cont, i))

def notasNull(notas, numPreg: List[int], irow: int) -> None:
    # Las primeras 4 columnas est\'an ocupadas.
    icol = 3
    for n in numPreg:
        for i in range(1,n+1):
            icol += 1
            notas.write(irow, icol, 0)
