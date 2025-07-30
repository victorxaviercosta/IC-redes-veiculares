import sumo_setup as sumo

from sim_logging import SimulationLogging

from abc import ABC, abstractmethod

class Simulation(ABC):
    """ The class that holds all simulation processes. """
    """ Handles a internal logging file that remain's open during simulation's execution. """

    def __init__(self,
                 config_file:str, add_files:str = "",
                 tripifo_out_file:str = "", log_file:str = "",
                 delay: int = 0,
                 gui:bool = False,
                 gui_settings_files:str = "",
                 auto_start:bool = False,
                 verbose:bool = False,
                 end_time:int = 3600,
                 sim_log_filename:str = "data/simulation.log"):
        """ Build a simulation by configuring the simulation parameters (see self.configure()) """
        
        self.configure(config_file, add_files, tripifo_out_file, log_file, delay, gui, gui_settings_files, auto_start, verbose, end_time)
        self.logging = SimulationLogging(sim_log_filename)


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
        """ Here's defined the logics to be executed before the first step of the simulation. """
        pass

    @abstractmethod
    def step(self) -> None:
        """ Here's defined the logics to be executed at each step of the simulation. """
        pass

    @abstractmethod
    def write_log(self) -> None:
        """ The logic for writing Simulation's log data should be implemented here. """
        pass

    def start(self) -> None:
        """ Starts a SUMO simulation via TraCI. The logic of the main loop is also defined here. """

        try:
            sumo.traci.start(self.sumo_config)

            self.logging.open()

            self.pre_start()

            # The loop must run while end_time is not reached and there is vehicles or persons on the network.
            while (sumo.traci.simulation.getTime() < self.end_time) and (sumo.traci.simulation.getMinExpectedNumber() > 0):
                self.step()
                sumo.traci.simulationStep()

            self.write_log()
            self.logging.log("Ending simulation.")
            self.logging.close()
            sumo.traci.close()

        except sumo.traci.exceptions.FatalTraCIError:
            self.write_log()
            print("[ERROR]: Simualation Ending on Exception: FatalTraCIError.")
            self.logging.write("[ERROR]: Simualation Ending on Exception: FatalTraCIError.")
            self.logging.close()
            sumo.traci.close()

        except sumo.traci.exceptions.TraCIException as excep:
            print(f"[ERROR]: TraCI exception: {excep}")
            self.logging.write(f"[ERROR]: TraCI exception: {excep}")
            self.logging.close()
            sumo.traci.close()


    def log(self, *args, **kwargs) -> None:
        """ A wrapper around SimulationLogging's log() method. """
        self.logging.log(*args, **kwargs)


if __name__ == "main":
    pass