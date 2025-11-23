"""
simulation/sim_logging.py
------------------------------

...
"""

import utils.sumo_setup as sumo
from domain.types import Volume
from params import LOGGING_LEVEL

from typing import TextIO, Any


class SimulationLogging():
    def __init__(self, log_filename: str):
        self.log_filename: str = log_filename
        self.log_file: TextIO = open(self.log_filename, "w")

    @staticmethod
    def printError(*args: Any, func_name: str = ""):
        """ Prints Error messages in a defined format """
        emsg: str = " ".join(map(str, args))
        if func_name:
            print(f"<ERROR> - [{func_name}]: {emsg}")
        else:
            print(f"<ERROR>: {emsg}")


    def open(self, mode: str = "a"):
        """ Opens the logging file in the specified mode """
        try:
            self.log_file = open(self.log_filename, mode)
        except IOError as error:
            self.printError(error, func_name=self.open.__name__)

    def close(self):
        """ Attempts closing the logging file """
        try:
            self.log_file.close()
            self.log_file = None
        except IOError as error:
            self.printError(error, func_name=self.close.__name__)

    def write(self, msg: str):
        try:
            self.log_file.write(msg)
        except IOError as error:
            self.printError(error, func_name=self.write.__name__)


    def log(self, *args: Any, **kwargs) -> None:
        """ 
            Register's the specified message in a defined format.
            Tries to write the message in the logging file as well.
            Volume specifies if the message should be registered according to the current LOGGING_LEVEL definition.
        """

        level: Volume = Volume.ESSENTIALS
        if "level" in kwargs:
            level = kwargs.pop("level")

        if level.value <= LOGGING_LEVEL.value:
            msg:str = f"[{sumo.traci.simulation.getTime()}] {" ".join(map(str, args))}"
            print(msg)

            if self.log_file:
                try:
                    self.log_file.write(msg + "\n")
                except IOError as error:
                    self.printError(error, func_name=self.log.__name__)



if __name__ == "__main__":
    pass