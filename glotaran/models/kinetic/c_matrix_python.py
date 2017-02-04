import numpy as np
from math import exp, sqrt, erf, erfc
from scipy.special import erfcx
class CMatrixPython(object):
    def c_matrix(self, rates, times, centers, widths, scale):
        raise NotImplementedError

    def c_matrix_gaussian_irf(self, C, rates, times, centers, widths, scale):
        calculateCMultiGaussian(C, rates, times, centers, widths,
                                scale)

def calculateCMultiGaussian(C,k,T,
                            centers, widths, scale):
    nr_gaussian = centers.shape[1]
    if nr_gaussian > 1:
        tmp = np.empty(C.shape, dtype=np.float64)
    J = centers.shape[0]
    for i in range(nr_gaussian):
        if i is 0:
            for j in range(J):
                calculateCSingleGaussian(C[j, :, :], k ,T, centers[j, i],
                                         widths[j, i], scale[i])
        else:
            for j in range(J):
                calculateCSingleGaussian(tmp[j, :, :], k ,T, centers[j, i],
                                         widths[j, i], scale[i])
            C += tmp

# Calculates exp(x*x) * erfc(x) but avoid under or overflow for large values of x
def erfce(x):
    #option 1 found here: http://stackoverflow.com/a/8963650
    #return erfcx1(x)
    #option 2 found here: http://stackoverflow.com/a/13995496
    return erfcx(x)

def erfcx1(x):
    if x < 25:
        return erfc(x) * exp(x * x)
    else:
        y = 1. / x
        z = y * y
        s = y * (1. + z * (-0.5 + z * (0.75 + z * (-1.875 + z * (6.5625 - 29.53125 * z)))))
        return s * 0.564189583547756287


def calculateCSingleGaussian(C, k,T,mu,
                  delta, scale):
    I = T.shape[0]
    J = k.shape[0]
    #  cdef double delta_tilde = delta / (2 * sqrt(2 * log(2)))
    #  with nogil, parallel(num_threads=num_threads):
    #      for i in prange(I, schedule=static):
    for i in range(I):
        for j in range(J):
            t_i = T[i]
            k_j = k[j]

            if k_j == 0:
                C[i, j] = 0
                continue

            alpha = -k_j * delta / sqrt(2)
            beta = (t_i - mu) / (delta * sqrt(2))
            thresh = beta - alpha
            if thresh < -1 :
                C[i, j] = scale * .5 * erfce(-thresh) * exp(-beta * beta)
            else:
                C[i, j] = scale * .5 * (1 + erf(thresh)) * exp(alpha * (alpha - 2 * beta))

     # print(np.isnan(C).any())