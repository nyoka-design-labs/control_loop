import numpy as np
import math
def fit_polynomial(data, interval, degree=3):
    """
    Fits a polynomial to the given data with uniform time intervals.

    Parameters:
    - data: A numpy array of data points.
    - interval: The uniform time interval between data points.
    - degree: The degree of the polynomial to fit.

    Returns:
    A function that calculates the modeled value for any given time.
    """
    # Generate the time array based on the data length and interval
    time = np.arange(0, len(data) * interval, interval)
    
    # Fit a polynomial of the specified degree to the data
    coeffs = np.polyfit(time, data, degree)
    
    # Create a polynomial function with the fitted coefficients
    poly_func = np.poly1d(coeffs)
    
    return poly_func


def exponential_func(T):

    u = -0.2
    x_0 = 500

    x = x_0 * math.exp(u * T)
    return x


def sigmoidal_func(T):
    a = 3
    b = 2
    c = 1

    x = a/(1+b*math.exp(-1*c*T))

    return x