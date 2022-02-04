def lista(f, inicio:int, fin:int, args:[float]) -> [float]:
    """ ls = [f(i, args) for i in range(inicio, fin+1)] """
    ls = [f(i, args) for i in range(inicio, fin+1)]
    return ls
