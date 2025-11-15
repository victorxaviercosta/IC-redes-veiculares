"""
exceptions.py
-------------

Defines custom Exceptions for the whole simulation framework.
"""
import inspect

class InterpreterException(Exception):
    def __init__(self, message=""):
        caller = inspect.stack()[1].function
        super().__init__(f"at [{caller}] : {message}")


class SimulationException(Exception):
    def __init__(self, message=""):
        super().__init__(message)
