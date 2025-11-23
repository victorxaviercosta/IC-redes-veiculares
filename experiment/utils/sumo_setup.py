"""
utils/sumo_setup.py
------------------------------

...
"""

import os, sys

# Guarantee that the path to SUMO tools are in the Python load path.
if 'SUMO_HOME' in os.environ:
    SUMO_TOOLS : str = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(SUMO_TOOLS)

    SUMO_GUI_BINARY : str = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo-gui.exe')
    SUMO_BINARY     : str = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo.exe')

else:
    sys.exit("Make sure the 'SUMO_HOME' enviroment variable exists")

import traci
import traci.constants as tc

from dataclasses import dataclass

@dataclass
class TraciParameters:
    sumocfg_file:str = ""
    add_files:str = ""
    tripinfo_out_file:str = ""
    sumo_log_file:str = ""
    gui_settings_files:str = ""
    delay: int = 0
    gui:bool = False
    auto_start:bool = False
    verbose:bool = False
    end_time:int = 3600