import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np

x = np.arange(12)
y = np.array([0, 0.1, 0.4, 3, 4, 5, 6, 7, 7.3, 7.5, 7.8, 8])

# weighted arithmetic mean (corrected - check the section below)
mean = sum(x * y) / sum(y)
sigma = np.sqrt(sum(y * (x - mean) ** 2) / sum(y))


def Logistic(x, L, x0, k):
    return L / (1 + np.exp(-1 * k * (x - x0)))


popt, pcov = curve_fit(Logistic, x, y, p0=[max(y), 5, 0.5])

plt.plot(x, y, 'b+:', label='data')
plt.plot(x, Logistic(x, *popt), 'r-', label='fit')
plt.legend()
plt.xlabel('Time (s)')
plt.ylabel('Y')
plt.show()

print(popt)