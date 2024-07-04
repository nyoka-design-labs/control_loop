class SerialPortNotFoundException(Exception):
    """Raised when the serial port could not be found"""
    pass

class TestDataCompleted(Exception):
    """Test Data Finished"""
    pass