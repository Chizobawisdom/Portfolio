# -*- coding: utf-8 -*-
"""
@ author: FORBAH ALISON, CHIZOBA WISDOM, ILEDIAGU DERA, AKINOLA DEBORAH,
CLINTON NGU

@Description: This program is calculating the roots of an arbitrary polynomial
function.

"""
# Declaration


import math
import random
import numpy as np
import matplotlib.pyplot as plt
import time


def poly(x, coeff):   # value of an arbitrary  polynomial function:
    # f(x) =  anx^n + an-1x^n-a...a1x + a0
    p = 0
    for coeffi in coeff:
        p = p*x + coeffi    # The factor of a given polynomial
    return p


def dpoly(coeff):   # input coeff. of a polynomial function
    # return coeff of the derivative of that function
    result = []
    n = len(coeff) - 1  # power of x
    for idx in range(n):
        result.append(coeff[idx] * (n - idx))  # derivative of each coefficient
        # f'(x) = annXn-1 + an-1n-1Xn-2 - a... a1X1-1 + 0
    return result


def solver(xi, coeff):  # roots of an arbitrary polynomial
    maxError = 1e-6
    error = math.inf
    while (error > maxError):  # Newton iteration
        df = poly(xi, dpoly(coeff))  # value of derivative of the polynomial
        if (df != 0):
            xn = xi - poly(xi, coeff)/df  # Newton-Raphson method
        else:
            xn = xi - poly(xi, coeff)/random.uniform(-1e-12, 1e-12)
        error = abs(xn - xi)
        xi = xn
        # it += 1
    return format(xn, '.4f')
    # ensure that roots are accurate to 4 decimal places


def real_roots():   # collects all the real roots
    roots = []
    result_poly = []
    time_out = time.time() + 15
    while (len(roots) < (len(ply2)-1)) and (time.time() < time_out):
        """iteration ends when the number of unique roots is equal to the
        highest power of x before the end of 15 seconds"""
        r2 = solver(iguess, ply2)  # roots of an arbitrary polynomial
        result_poly.append(r2)
        roots = set(result_poly)  # collects unique roots
    return roots


# Input


ply2 = []
order = int(input("Enter highest degree of x: "))
while (order < 2):
    print("2-degree Polynomials and above only!")
    order = int(input("Enter highest degree of x: "))
else:
    for a in range(-1, order):
        print("\n""Input coefficient of X with degree ", abs(a-order)-1,
              " and press the return key:")
        i = float(input())
        ply2.append(i)
    x = np.arange(-4, 4, 0.01)  # evenly spaced values on the x-axis
    fx_2 = poly(x, ply2)
    plt.plot(x, fx_2, 'b')  # plots the graph with a blue curve
    plt.grid(True)
    plt.show()
iguess = float(input("Guess a root: "))


# Processing


def num_roots():
    display = []
    discriminant = ((ply2[1]) ** 2) - 4*(ply2[0])*(ply2[2])
    # discriminant == b**2 - 4ac
    if (len(ply2) == 3) and (discriminant < 0):
        """when b**2 - 4ac from the quadratic formula is less than zero,
        then the equation has no real roots"""
        display.append("The function has no real roots.")
    else:
        display.append(real_roots())
    return display


# Output


print(num_roots())  # display all the real roots
