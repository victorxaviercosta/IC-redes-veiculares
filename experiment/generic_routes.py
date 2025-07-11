import sumo_setup as sumo
import os, sys
import subprocess
import argparse

RANDOM_TRIP_TOOL: str = os.path.join(sumo.SUMO_TOOLS, "randomTrips.py")

class GenericRouteGenerator:
    """
    Holds the definitions for generating a SUMO route without v_types.
    """

    def __init__(self, net_file:str, output_file:str, output_trip_file:str, num_trips:int=10, period:float=1.0, prefix:str=""):
        self._net_file: str = net_file                  # Input net file path.
        self._output_file: str = output_file            # Output route file path.
        self._output_trip_file: str = output_trip_file  # Output trip file path.
        self._num_trips: int= num_trips                 # Number of trips to be generated.
        self._period: float = period                    # To generate vehicles with equidistant departure times (default 1.0).   
        self._end_time: int = num_trips * period        # End time (default 3600)
        self._prefix: str = prefix                      # Prefix for the trip ids
        self._vehicle_class: str = "pedestrian"         # The vehicle class assigned to the generated trips (adds a standard vType definition to the output_file).

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
        print(f"Route file '{self._output_file}' generated (without vTypes).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates a route file for SUMO simulations without specific vTypes.")
    parser.add_argument("-i", "--input-file", type=str, default="config/cologne2.net.xml", help="SUMO net.xml input file path.")
    parser.add_argument("-o", "--output-file", type=str, default="config/routes.rou.xml", help="SUMO rou.xml output file path.")
    parser.add_argument("-ot", "--output-trip-file", type=str, default="config/trips.trips.xml", help="SUMO trips.xml output file path.")
    parser.add_argument("-n", "--num-trips", type=int, default=100, help="Number of trips to be generated.")
    parser.add_argument("-dt", "--period", type=float, default=1.0, help="To generate vehicles with equidistant departure times")
    parser.add_argument("-p", "--prefix", type=str, default="", help="Prefix for the trip ids.")

    args = parser.parse_args()

    route = GenericRouteGenerator(args.input_file, args.output_file, args.output_trip_file, args.num_trips, args.period, args.prefix)
    route()