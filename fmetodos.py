import math
import fmatriz
from fractions import Fraction

w0 = 11
w1 = 81
w2 = -64

def newton(f, fp, x0, nmax = math.inf, eps = 1e-16) -> float:
    """ M\'etodo de Newton. 

    Argumentos
    ----------

    f:
        Funcion.
    fp:
        Derivada.
    x0:
        Aproximación inicial.
    nmax:
        Máximo número de iteraciones.
    eps:
        Error m\'aximo
    """
    xn: float = x0
    err: float = 1
    fxn = f(x0)
    while (nmax > 0 and err > eps):
        x0 = xn
        fx0 = fxn
        nmax -= 1
        fpx0 = fp(x0)
        xn = x0 - f(x0) / fp(x0)
        fxn = f(xn)
        err = abs(fxn)
    return xn


def derivada(f, x0, n=1, delta=1e-6):
    assert(delta > 0)
    delta = delta ** (1/n)
    if n == 0:
        return f(x0)
    elif n == 1:
        return (f(x0+delta) - f(x0-delta)) / (2 * delta)
    elif n == 2:
        return (f(x0+delta) - 2 * f(x0) + f(x0-delta)) / (delta * delta)
    elif n == 3:
        return (f(x0 + 2 * delta) - 2 * f(x0 + delta) + 2 * f(x0 - delta) - f(x0 - 2 * delta)) / (2 * delta**3)
    elif n == 4:
        return (f(x0 + 2 * delta) - 4 * f(x0 + delta) + 6 * f(x0) - 4 * f(x0 - delta) + f(x0 - 2 * delta)) / delta**4
    else:
        return math.nan


def integral(f, a, b, eps = 1e-12, prof = math.inf):
    m = 0.5 * (b - a)
    k = 0.5 * (a + b)
    ys = [f(-m + k), f(-m/3 + k), f(k), f(m/3+k), f(m+k)]
    aprox = m * (w0 * ys[0] + w1 * ys[1] + w2 * ys[2] + w1 * ys[3] + w0 * ys[4]) / 60
    return _integral_rec(f, a, b, eps, prof, ys, aprox)

def _integral_rec(f, a, b, eps, prof, ys, aprox):
    m = 0.5 * (b - a)
    k = 0.5 * (a + b)

    a1 = a
    b1 = k
    m = m / 6
    k1 = 0.5 * (a1 + b1)
    y1 = [ys[0], f(-m + k1), f(k1), ys[1], ys[2]]
    I1 = m * (w0 * y1[0] + w1 * y1[1] + w2 * y1[2] + w1 * y1[3] + w0 * y1[4]) / 20

    a2 = k
    b2 = b
    k2 = 0.5 * (a2 + b2)
    y2 = [ys[2], ys[3], f(k2), f(m + k2), ys[4]]
    I2 = m * (w0 * y2[0] + w1 * y2[1] + w2 * y2[2] + w1 * y2[3] + w0 * y2[4]) / 20

    ap2 = I1 + I2
    if ap2 == 0:
        err = abs(aprox)
    else:
        err = abs((ap2 - aprox)/ap2)

    if err > eps and prof > 0:
        I1 = _integral_rec(f, a1, b1, eps, prof - 1, y1, I1)
        I2 = _integral_rec(f, a2, b2, eps, prof - 1, y2, I2)
        ap2 = I1 + I2

    return ap2


def cuadratica(a, b, c):
    disc = b**2 - 4 * a * c
    assert(disc >= 0)
    disc = math.sqrt(disc)
    exp = -b + math.copysign(disc, -b)
    exp = round(exp) if round(exp) == exp else exp
    return (exp / (2 * a), 2 * c / exp) if isinstance(exp, float) else (Fraction(exp, 2*a), Fraction(2*c, exp))


def cero(f, a, b):
    m = 0.5 * (a + b)
    fa, fm, fb = f(a), f(m), f(b)
    assert(fa * fb < 0)
    while True:
        rhs = [fa, fm, fb]
        A = [[a*a, a, 1], [m*m, m, 1], [b * b, b, 1]]
        ax, bx, cx = matriz.sistema(A, rhs)
        x1, x2 = cuadratica(ax, bx, cx)
        if fa * fm <= 0:
            b = m
            fb = fm
        else:
            a = m
            fa = fm
        print(('a, fa, b, fb, x1, x2', a, fa, b, fb, x1, x2))
        if a <= x1 and x1 <= b:
            f1 = f(x1)
            if a < x2 and x2 < b:
                f2 = f(x2)
                _, p, fp = min((abs(f1), x1, f1), (abs(f2), x2, f2))
            else:
                p, fp = x1, f1
        else:
            assert(a <= x2 and x2 <= b)
            p, fp = x2, f(x2)
        print(('p, fp', p, fp))
        if abs(fp) < 1e-16:
            return p
        if fa * fp < 0:
            b = p
            fb = fp
        else:
            a = p
            fa = fp
        m = 0.5 * (a + b)
        fm = f(m)

def fmin(f, aa: float, bb: float, tries: int = 3, eps: float = 1e-6, delta = 0.5) -> tuple[float, float]:
    A: set = set([aa, bb])
    B: set
    C: set
    X: list[float]
    fmin: float
    xmin: float
    fmin, xmin = min((f(aa), aa), (f(bb), bb))
    npart: int = 1
    jump: float = bb - aa
    dif: float = (bb - aa)
    vals: list[float]
    ntries: int = 0
    x1: float
    x2: float
    x3: float
    vx: float
    vy: float
    while ntries < tries:
        ntries += 1
        npart = 2 * npart
        jump *= 0.5
        delta = min(delta, 0.5 * jump)
        B = set([aa + x * dif / npart for x in range(npart + 1)])
        C = B.difference(A)
        A = B

        for x2 in C:
            fx2 = f(x2)
            x1 = x2 - delta
            fx1 = f(x1)
            x3 = x2 + delta
            fx3 = f(x3)
            fmin, xmin = min([(fx1, x1), (fx2, x2), (fx3, x3), (fmin, xmin)])
            while True:
                f1 = (fx2 - fx1) / (x2 - x1)
                f2 = (fx3 - fx2) / (x3 - x2)
                a = (f2 - f1) / (x3 - x1)
                if a <= 0:
                    break
                b = f1 - a * (x1 + x2)
                vx = -b / (2*a)
                if vx <= x1 or vx >= x3:
                    break
                c = fx1 + x1 * (x2 * a - f1)
                disc = b**2 - 4 * a * c
                vy = -disc / (4*a)
                if vy < fmin:
                    if abs((fmin - vy) / vy) < eps:
                        ntries = 0
                    fmin = vy
                    xmin = vx
                if abs(vx-x2) * delta < eps:
                    break
                if vx < x2:
                    x3 = x2
                    fx3 = fx2
                else:
                    x1 = x2
                    fx1 = fx2
                x2 = vx
                fx2 = vy
    return (xmin, fmin)

def regresionLineal(xs: list[float], ys: list[float], fx=None, gy=None):
    """ Aplica regresi\'on lineal a los datos. fx y gy son funciones
    que aplica previo a la regresi\'on. Devuelve (m, b), la pendiente
    y la intersecci\'on con el eje y. """
    n = len(xs)
    assert(n == len(ys))
    if not fx == None:
        xs = [fx(xi) for xi in xs]
    if not gy == None:
        ys = [gy(y) for y in ys]
    sumxi = sum(xs)
    sumyi = sum(ys)
    sumx2 = sum([x**2 for x in xs])
    sumxy = sum([xs[i] * ys[i] for i in range(n)])
    m = (n * sumxy - sumxi * sumyi) / (n * sumx2 - sumxi**2)
    b = (sumyi - m * sumxi) / n
    return (m, b)
