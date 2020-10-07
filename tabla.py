def encabezadoNotas(notas, numPregs: int) -> None:
    notas.set_column('A:A', 15)
    notas.set_column('B:B', 35)
    notas.set_column('C:C', 15)
    notas.write(0, 0, '# de carnet')
    notas.write(0, 1, 'Nombre')
    notas.write(0, 2, 'Usuario')
    notas.write(0, 3, 'Nota')
    notas.write(0, 4, 'Puntaje')
    # Las primeras 5 columnas est\'an ocupadas.
    for i in range(numPregs):
        notas.write(0, i + 5, 'Preg. %d' % (i + 1))


def notasNull(notas, numPregs: int, irow: int) -> None:
    # Las primeras 5 columnas est\'an ocupadas.
    for i in range(numPregs):
        notas.write(irow, i + 5, 0)
