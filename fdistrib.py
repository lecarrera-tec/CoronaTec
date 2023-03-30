import math
import fmetodos

def hiper(k: int, n: int, exitos: int, r: int):
    """ P (X = k) """
    return math.comb(exitos, k) * math.comb(n - exitos, r - k) / math.comb(n, r)

def hiperAcum(k: int, n: int, exitos: int, r: int, izq = 0):
    """ P(X <= k) """
    return sum([math.comb(exitos, x) * math.comb(n-exitos, r-x) for x in range(izq, k+1)]) / math.comb(n, r)

def binomAcumInv(n, p, t):
    """
    Calcula el m\'aximo valor de $k$, tal que un par\'ametro 
    t \in (0, 1] satisfaga que:
    t \geq \sum_{x=0}^k C(n, x) p**x * (1-p)**(n-x)
    """
    q = 1 - p
    if n * p > 5 and n * q > 5:
        k = math.floor(math.sqrt(n * p * q) * phiInv(t) + n * p)
    else:
        k = 0
    suma = sum([math.comb(n, x) * p**x * q**(n-x) for x in range(k+1)])
    while k > 0 and suma > t:
        suma -= math.comb(n, k) * p**k * q**(n-k)
        k -= 1
    nuevo = math.comb(n, k) * p**k * q**(n-k)
    while suma + nuevo <= t:
        suma += nuevo
        k += 1
        nuevo = math.comb(n, k) * p**k * q**(n-k)
    return k

def phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x/math.sqrt(2)))


def normal(z, mu, sigma):
    z = (z - mu) / sigma
    return phi(z)


def phiInv(p: float) -> float:
    assert(0 <= p and p <= 1)
    signo = 1
    if p > 0.5:
        signo = -1
        p = 1 - p
    f = lambda x: phi(x) - p
    fp = lambda x: math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)
    return signo * fmetodos.newton(f, fp, 0)


def gamma(x, alfa, beta):
    if beta > 1:
        x = x / beta
        beta = 1
    f = lambda x: x**(alfa - 1) * math.exp(-x/beta) / ((beta ** alfa) * math.gamma(alfa))
    return fmetodos.integral(f, 0, x, 1e-6, 20)


def gammaInv(p, alfa, beta):
    f = lambda x: gamma(x, alfa, beta) - p
    fp = lambda x: x**(alfa - 1) * math.exp(-x/beta) / ((beta ** alfa) * math.gamma(alfa))
    return fmetodos.newton(f, fp, 5)

