import numpy as np

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

# Example usage:
data = np.random.rand(10)  # Example data points
interval = 1  # Example time interval between data points
