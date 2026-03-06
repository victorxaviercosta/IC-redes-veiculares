"""
runner.py
------------------------------

...
"""

from dataclasses import dataclass


from .params import (
    # === Default parameters:
    DEFAULT_CSADD_FILENAME,

    DEFAULT_INITIAL_LOG_FILENAME,
    DEFAULT_VALIDATION_LOG_FILENAME,

    MAX_STATIONS,
    MIN_STATIONS_PER_CELL,
    DEFAULT_GRID_SIZE
)

from .simulation import ev_simulation as evs
from .tools.cs_deposition import Interpreter, LS_Methods
from .graphs.network_graph import NetworkGraph
from .utils.sumo_setup import TraciParameters
from .domain.types import SimStatistics
from .domain import colors


# === Data Classes:

@dataclass
class SimulationParameters():
    initial_log_filename:    str = DEFAULT_INITIAL_LOG_FILENAME
    validation_log_filename: str = DEFAULT_VALIDATION_LOG_FILENAME
    add_file:                str = DEFAULT_CSADD_FILENAME
    max_stations:            int = MAX_STATIONS
    min_stations_per_cell:   str = MIN_STATIONS_PER_CELL
    method:                  LS_Methods = LS_Methods.RANDOM
    grid_size:               int = DEFAULT_GRID_SIZE


# === Simulation Controllers

class Runner():
    def __init__(self, params: TraciParameters, sim_params: SimulationParameters):
        self.params: TraciParameters = params
        self.sim_params: SimulationParameters = sim_params

        self.net_file = get_network_file(params.sumocfg_file)


    def initial_run(self) -> None:
        self.params.add_files = ""

        self.net_graph : NetworkGraph = NetworkGraph(self.net_file, {}, self.sim_params.grid_size)
        simulation: evs.Simulation = evs.EV_Simulation( params = self.params, sim_log_filename = self.sim_params.initial_log_filename, net_graph = self.net_graph )

        print(f"\n{colors.FG_GREEN}>>> Starting Initial Run:{colors.RESET} (Ending at {self.params.end_time})\n")
        simulation.start()


    def validation_run(self) -> SimStatistics:
        print(f"{colors.FG_YELLOW}\nStarting CS deposition: \n{colors.RESET}")

        interpreter: Interpreter = Interpreter(log_filename=self.sim_params.initial_log_filename, output_filename=self.sim_params.add_file, 
                                               max_stations = self.sim_params.max_stations, min_stations_per_cell = self.sim_params.min_stations_per_cell)
        interpreter(net_file = self.net_file, grid_size=self.sim_params.grid_size, method=self.sim_params.method)
        self.net_graph : NetworkGraph = interpreter.net_graph
        self.net_graph.show(with_labels=False)

        self.params.add_files = self.sim_params.add_file
        simulation: evs.Simulation = evs.EV_Simulation( params = self.params, sim_log_filename = self.sim_params.validation_log_filename, net_graph = self.net_graph )

        print(f"\n{colors.FG_GREEN}>>> Starting Validation Run:{colors.RESET} (Ending at {self.params.end_time})\n")
        simulation.start()

        return simulation.stats



def get_network_file(sumocfg_file : str) -> str :
    import xml.etree.ElementTree as ET
    import os

    path = os.path.dirname(sumocfg_file)

    xml_tree: ET.ElementTree[ET.Element[str]] = ET.parse(sumocfg_file)
    xml_root: ET.Element[str] = xml_tree.getroot()

    input: ET.Element[str] = xml_root.find("input")

    return f"{path}/{input.find("net-file").get("value")}"
