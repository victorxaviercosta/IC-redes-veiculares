import sumo_setup as sumo
from abc import ABC, abstractmethod

class Simulation(ABC):
    """ The class that holds all simulation processes."""

    def __init__(self,
                 config_file:str, add_files:str = "",
                 tripifo_out_file:str = "", log_file:str = "",
                 delay: int = 0,
                 gui:bool = False,
                 gui_settings_files:str = "",
                 auto_start:bool = False,
                 verbose:bool = False,
                 end_time:int = 3600):
        """ Build a simulation by configuring the simulation parameters (see self.configure()) """
        
        self.configure(config_file, add_files, tripifo_out_file, log_file, delay, gui, gui_settings_files, auto_start, verbose, end_time)


    def configure(self,
                  config_file:str, add_files:str = "",
                  tripifo_out_file:str = "", log_file:str = "",
                  delay: int = 0,
                  gui:bool = False,
                  gui_settings_files:str = "",
                  auto_start:bool = False,
                  verbose:bool = False,
                  end_time:int = 3600) -> None:
        """ Defines the sumo simulator configuration options according to the given arguments. """
        
        self.end_time = end_time
        self.sumo_binary:str = sumo.SUMO_GUI_BINARY if gui else sumo.SUMO_BINARY
        self.sumo_config:list[str] = [
            self.sumo_binary,
            "--configuration-file", config_file,
            "--delay", str(delay)
        ]

        if add_files:           self.sumo_config.extend(["--additional-files", add_files])
        if tripifo_out_file:    self.sumo_config.extend(["--tripinfo-output", tripifo_out_file])
        if log_file:            self.sumo_config.extend(["--log", log_file])
        if gui_settings_files:  self.sumo_config.extend(["--gui-settings-file", gui_settings_files])
        if auto_start:          self.sumo_config.append("--start")
        if verbose:             self.sumo_config.append("--verbose")


    @abstractmethod
    def pre_start(self) -> None:
        """ Here's defined the logics to be executed before the firts step of the simulation """
        pass


    @abstractmethod
    def step(self) -> None:
        """ Here's defined the logics to be executed at each step of the simulation """
        pass


    def start(self) -> None:
        """ Starts a SUMO simulation via TraCI. The logic of the main loop is also defined here. """

        sumo.traci.start(self.sumo_config)

        # TODO: rethink the pre-start method since it seems just not to make sense.
        #sumo.traci.simulationStep() # Initializing simultation.
        #self.pre_start()

        # The loop must run while end_time is not reached and there is vehicles or persons on the network.
        while (sumo.traci.simulation.getTime() < self.end_time) and (sumo.traci.simulation.getMinExpectedNumber() > 0):
            self.step()
            sumo.traci.simulationStep()

        Simulation.log("Ending simulation.")
        sumo.traci.close()

    @staticmethod
    def log(*args) -> None:
        msg:str = " ".join(map(str, args))
        print(f"[{sumo.traci.simulation.getTime()}] {msg}")



if __name__ == "main":
    pass