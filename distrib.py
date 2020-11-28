import math
import metodos

def phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x/math.sqrt(2)))


def normal(z, mu, sigma):
    z = (z - mu) / sigma
    return phi(z)


def phiInv(p: float) -> float:
    assert(0 <= p and p <= 1)
    f = lambda x: phi(x) - p
    fp = lambda x: math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)
    return metodos.newton(f, fp, 0)


def gamma(x, alfa, beta):
    if beta > 1:
        beta = 1
        x = x / beta
    f = lambda x: x**(alfa - 1) * math.exp(-x/beta) / ((beta ** alfa) * math.gamma(alfa))
    return metodos.integral(f, 0, x, [], 0, 1e-6, 20)


def gammaInv(p, alfa, beta):
    f = lambda x: gamma(x, alfa, beta) - p
    fp = lambda x: x**(alfa - 1) * math.exp(-x/beta) / ((beta ** alfa) * math.gamma(alfa))
    return metodos.newton(f, fp, 5)
