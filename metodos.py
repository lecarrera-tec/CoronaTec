import math
import matriz

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


def integral(f, a, b, ys = [], aprox = 0, eps = 1e-12, prof = math.inf):
    m = 0.5 * (b - a)
    k = 0.5 * (a + b)
    if len(ys) == 0:
        ys = [f(-m + k), f(-m/3 + k), f(k), f(m/3+k), f(m+k)]
        aprox = m * (w0 * ys[0] + w1 * ys[1] + w2 * ys[2] + w1 * ys[3] + w0 * ys[4]) / 60

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
    err = abs((ap2 - aprox)/ap2)

    if err > eps and prof > 0:
        I1 = integral(f, a1, b1, y1, I1, eps, prof - 1)
        I2 = integral(f, a2, b2, y2, I2, eps, prof - 1)
        ap2 = I1 + I2
    return ap2


def cuadratica(a, b, c):
    disc = b * b - 4 * a * c
    assert(disc >= 0)
    b = -b
    exp = math.copysign(b, disc)
    return (exp / 2 * a, 2 * c / exp)


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
