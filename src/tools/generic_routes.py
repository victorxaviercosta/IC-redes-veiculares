# src/tools/generic_routes.py
# -----------------------------------------------------------

# Defines a idependent helper driver to generate generic SUMO routes (routes of vehicles without specific vtypes)
# according to the given .net.xml file.

# Uses SUMO's randomTrips.py to generate the vehicle's routes.

# ===========================================================

import os, sys
import subprocess
import argparse

from ..utils import sumo_setup as sumo

RANDOM_TRIP_TOOL: str = os.path.join(sumo.SUMO_TOOLS, "randomTrips.py")

class GenericRouteGenerator:
    """
    Holds the definitions for generating a SUMO route without v_types.
    """

    def __init__(self, net_file:str, output_file:str, output_trip_file:str, num_trips:int=10, period:float=1.0, prefix:str="", force0: bool = False):
        self._net_file: str = net_file                  # Input net file path.
        self._output_file: str = output_file            # Output route file path.
        self._output_trip_file: str = output_trip_file  # Output trip file path.
        self._num_trips: int= num_trips                 # Number of trips to be generated.
        self._period: float = period                    # To generate vehicles with equidistant departure times (default 1.0).   
        self._end_time: int = num_trips * period        # End time (default 3600)
        self._prefix: str = prefix                      # Prefix for the trip ids
        self._vehicle_class: str = "passenger"          # The vehicle class assigned to the generated trips (adds a standard vType definition to the output_file).
        self._force0: bool = force0                     # 

    def __call__(self) -> None:
        cmd = [
            sys.executable,
            RANDOM_TRIP_TOOL,
            "-n", self._net_file,
            "-r", self._output_file,
            "-o", self._output_trip_file,
            "-e", str(self._end_time),
            "-p", str(self._period),
            "--vehicle-class", self._vehicle_class,
            "--prefix", self._prefix
        ]


        subprocess.run(cmd, check=True)

        if self._force0:
            self._force_depart_zero()

        print(f"Route file '{self._output_file}' generated (without vTypes).")



    def _force_depart_zero(self):
        import xml.etree.ElementTree as ET
        tree = ET.parse(self._output_file)
        root = tree.getroot()

        for vehicle in root.findall("vehicle"):
            vehicle.set("depart", "0")
            vehicle.set("departLane", "best")
            vehicle.set("departSpeed", "max")

        tree.write(self._output_file, encoding="UTF-8", xml_declaration=True)

        print("All vehicle depart times forced to 0.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates a route file for SUMO simulations without specific vTypes.")
    parser.add_argument("-wd", "--working-directory", default=".", type=str, help="The working directory where to look for input files and store output files.")
    parser.add_argument("-i", "--input-file", type=str, help="SUMO net.xml input file path.")
    parser.add_argument("-o", "--output-file", type=str, help="SUMO rou.xml output file path.")
    parser.add_argument("-ot", "--output-trip-file", type=str, default="trips.trips.xml", help="SUMO trips.xml output file path.")
    parser.add_argument("-n", "--num-trips", type=int, default=100, help="Number of trips to be generated.")
    parser.add_argument("-dt", "--period", type=float, default=0.2, help="To generate vehicles with equidistant departure times")
    parser.add_argument("-p", "--prefix", type=str, default="veh", help="Prefix for the trip ids.")
    parser.add_argument("-f0", "--force0", action="store_true", help="Wheter the vehicles should be forced to depart at 0.")

    args = parser.parse_args()

    args.input_file = f"{args.working_directory }/{args.input_file}"
    args.output_file = f"{args.working_directory }/{args.output_file}"
    args.output_trip_file = f"{args.working_directory }/{args.output_trip_file}"
    route = GenericRouteGenerator(args.input_file, args.output_file, args.output_trip_file, args.num_trips, args.period, args.prefix, args.force0)
    route()