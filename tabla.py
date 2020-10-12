def encabezadoNotas(notas, n: int) -> None:
    notas.set_column('A:A', 15)
    notas.set_column('B:B', 35)
    notas.set_column('C:C', 15)
    notas.write(0, 0, '# de carnet')
    notas.write(0, 1, 'Nombre')
    notas.write(0, 2, 'Usuario')
    notas.write(0, 3, 'Nota')
    notas.write(0, 4, 'Puntaje')
    # Las primeras 5 columnas est\'an ocupadas.
    for i in range(n):
        notas.write(0, i + 5, 'Preg. %d' % (i + 1))


def notasNull(sheet, numPregs: int, irow: int, pts: int, bold) -> None:
    # Las primeras 5 columnas est\'an ocupadas.
    for i in range(numPregs):
        sheet.write(irow, i + 5, 0)
    # Se suman los puntos ;)
    formula = '=SUM(F%d:%c%d)'\
              % (irow + 1,
                 chr(ord('F') + numPregs - 1),
                 irow + 1)
    sheet.write(irow, 4, formula)
    # y se calcula la nota
    formula = '= 100 * E%d / %d' % (irow + 1, pts)
    sheet.write(irow, 3, formula, bold)
    sheet.write(irow, 2, 'ausente')
