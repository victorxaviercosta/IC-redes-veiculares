# src/domain/exceptions.py
# -----------------------------------------------------------

# Defines some custom Exceptions for the simulation's framework.

# ===========================================================

import inspect

class InterpreterException(Exception):
    def __init__(self, message=""):
        caller = inspect.stack()[1].function
        super().__init__(f"at [{caller}] : {message}")


class SimulationException(Exception):
    def __init__(self, message=""):
        super().__init__(message)
