"""
simulation/simulation.py
------------------------------

...
"""

import utils.sumo_setup as sumo
from .sim_logging import SimulationLogging
from domain.types import LaneData
from graphs.network_graph import NetworkGraph
from params import DEFAULT_LOGS_DIRECTORY, SHOW_GRAPH

from abc import ABC, abstractmethod

class Simulation(ABC):
    """ The class that holds all simulation processes. """
    """ Handles a internal logging file that remain's open during simulation's execution. """
    
    def __init__(self, params : sumo.TraciParameters, sim_log_filename : str, net_graph : NetworkGraph):    
        """ Build a simulation by configuring the simulation parameters (see self.configure()) """

        self.configure(params)
        self.logging = SimulationLogging(f"{DEFAULT_LOGS_DIRECTORY}{sim_log_filename}")
        self.base_filename: str = sim_log_filename.split(".")[0]

        self.net_graph : NetworkGraph = net_graph

        if SHOW_GRAPH:
            self.net_graph.show()

    def configure(self, params: sumo.TraciParameters) -> None:
        """ Defines the sumo simulator configuration options according to the given TraCI parameters. """
        
        self.end_time:int = params.end_time
        sumo_binary:str = sumo.SUMO_GUI_BINARY if params.gui else sumo.SUMO_BINARY
        self.sumo_config:list[str] = [
            sumo_binary,
            "--configuration-file", params.sumocfg_file,
            "--delay", str(params.delay)
        ]

        if params.route_files:         self.sumo_config.extend(["--route-files", params.route_files])
        if params.add_files:           self.sumo_config.extend(["--additional-files", params.add_files])
        if params.tripinfo_out_file:   self.sumo_config.extend(["--tripinfo-output", f"{DEFAULT_LOGS_DIRECTORY}{params.tripinfo_out_file}"])
        if params.sumo_log_file:       self.sumo_config.extend(["--log", f"{DEFAULT_LOGS_DIRECTORY}{params.sumo_log_file}"])
        if params.gui_settings_files:  self.sumo_config.extend(["--gui-settings-file", params.gui_settings_files])
        if params.auto_start:          self.sumo_config.append("--start")
        if params.verbose:             self.sumo_config.append("--verbose")

    @abstractmethod
    def pre_start(self) -> None:
        """ Here's defined the logics to be executed before the first step of the simulation. """
        pass

    @abstractmethod
    def step(self) -> None:
        """ Here's defined the logics to be executed at each step of the simulation. """
        pass

    @abstractmethod
    def post_end(self) -> None:
        """ Here's defined the logics to be executed after the last step of the simulation. """
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

            self.post_end()

            self.finish("Ending simulation.")

        except sumo.traci.exceptions.FatalTraCIError:
            self.finish("[ERROR]: Simualation Ending on Exception: FatalTraCIError.")

        except sumo.traci.exceptions.TraCIException as excep:
            self.finish(f"[ERROR]: TraCI exception: {excep}", write_log=False)


    def finish(self, end_msg: str, write_log: bool = True) -> None:
        """ Finishes the simulation closing logging files and traci's connection. """

        if write_log:
            self.write_log()
        print(end_msg)
        self.logging.write(end_msg)
        self.logging.close()
        sumo.traci.close()


    def log(self, *args, **kwargs) -> None:
        """ A wrapper around SimulationLogging's log() method. """
        self.logging.log(*args, **kwargs)


if __name__ == "main":
    pass