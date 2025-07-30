import sumo_setup as sumo
from typing import TextIO, Any
from dataclasses import dataclass

#
@dataclass(frozen=True)
class LogParameters():
    # ===< Volume levels >===
    ESSENTIALS: int = 0
    UTILS: int = 1
    SPECIFICS: int = 2
    ALL:int = 3

    # ===< Logging options >===
    LOG_BATTERY_PERIOD:int = 500 # [s]
    LOG_CHARGE_LEVEL: bool = False
    LOG_STATION_DISTANCES: bool = False
    LOG_END_OF_ROUTE_REROUTE: bool = False

    # ===< DEFINED_LEVELS >===
    LOGGING_LEVEL: int = ESSENTIALS


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

        level: str = 0
        if "level" in kwargs:
            level = kwargs.pop("level")

        if level <= LogParameters.LOGGING_LEVEL:
            msg:str = f"[{sumo.traci.simulation.getTime()}] {" ".join(map(str, args))}"
            print(msg)

            if self.log_file:
                try:
                    self.log_file.write(msg + "\n")
                except IOError as error:
                    self.printError(error, func_name=self.log.__name__)



if __name__ == "__main__":
    pass