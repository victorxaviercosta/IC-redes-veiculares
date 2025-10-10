import xml.etree.ElementTree as ET
import random
import argparse

from sim_tools import VEHICLES_LENGTH

# Default Argument Values
DEFAULT_WORKING_DIRECTORY: str = "."
DEFAULT_INPUT_FILE: str = "routes.rou.xml"
DEFAULT_PERCENTAGES: list[float] = [0.05, 0.10, 0.20]
DEFAULT_NUM_FILES: int = 5
DEFAULT_BATTERY_CAPACITY: float = 64000

#
NORMAL_VTYPE: dict[str, str] = {
    "id": "normal_vehicle",
    "length": f"{VEHICLES_LENGTH}",
    "accel": "2.6",
    "decel": "4.5",
    "sigma": "0.5",
    "maxSpeed": "50",
    "color": "0.5,0.5,0.5"
}

ELECTRIC_VTYPE: dict[str, str] = {
    "id": "electric_vehicle",
    "length": f"{VEHICLES_LENGTH}",
    "accel": "2.6",
    "decel": "4.5",
    "sigma": "0.5",
    "maxSpeed": "50",
    "mass": "1036.00",
    "color": "0,1,0",
    "emissionClass": "Energy/default"
}

# soulEV65 parameters
EV_PARAMS: dict[str, str] = {
    "has.battery.device": "true",
    "device.battery.capacity": f"{DEFAULT_BATTERY_CAPACITY}",   # float - [Wh]
    "device.battery.maximumChargeRate": "150000",       # float - [W]
    "maximumPower": "150000",                           # float - [W]
    "airDragCoefficient": "0.35",                       # float
    "constantPowerIntake": "100",                       # float - [W] Avg. (constant) power of consumers
    "frontSurfaceArea": "2.6",                          # float - [m^2]
    "propulsionEfficiency": "0.98",                     # float - Drive efficiency
    "radialDragCoefficient": "0.1",                     # float
    "recuperationEfficiency": "0.96",                   # float
    "rollDragCoefficient": "0.01",                      # float - How much resistance a rolling object experiences.
    "stoppingThreshold": "0.1",                         # float - Maximum velocity to start charging
    "rotatingMass": "40"                                # float [kg]
}

class EVDefiner:
    def __init__(self):
        pass
        
    def _add_vtypes(self, root:ET.Element, battery_capacity:int) -> None:
        """ Checks if vTypes for Normal and Electric vehicles are defined. Defines it if not. """

        # In case there's any Normal Vehicle in the Routes file.
        if root.find("vType[@id=\"normal_vehicle\"]") == None:
            vtype_normal = ET.Element(
                "vType", attrib= NORMAL_VTYPE
            )
            root.insert(0, vtype_normal)
        
        # In case there's any Electric Vehicle in the Routes file.
        if root.find("vType[@id=\"electric_vehicle\"]") == None:

            EV_PARAMS["device.battery.capacity"] = f"{battery_capacity}"
            vtype_electric = ET.Element("vType", ELECTRIC_VTYPE)

            for key, value in EV_PARAMS.items():
                ET.SubElement(vtype_electric, "param", {"key": key, "value": value})

            root.insert(0, vtype_electric)

    def define(self, input_file:str, output_file:str, ev_percentage:float, battery_capacity:int) -> None:
        """ Modifies a route file to define a percentage of the trips as ev trips selected randomly. """

        tree: ET.ElementTree[ET.Element[str]] = ET.parse(input_file)
        root: ET.Element[str] = tree.getroot()

        self._add_vtypes(root, battery_capacity)

        all_vehicles:list[ET.Element[str]] = root.findall("vehicle")    # Getting all vehicles.

        n_vehicles:int = len(all_vehicles)                  # Getting total number of vehicles.
        n_electric:int = int(n_vehicles * ev_percentage)    # Calculating the number of electric vehicles.

        all_electric:list[ET.Element[str]] = random.sample(all_vehicles, n_electric)  # Selecting vehicles to convert into electric randomly.

        # Changing vTpye for electric vehicles.
        for vehicle in all_vehicles:
            if vehicle in all_electric:
                vehicle.set("type", "electric_vehicle")
            else:
                vehicle.set("type", "normal_vehicle")

        tree.write(output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Modifies the given input SUMO rou.xml file to define the given percentage of the trips as electric vehicle trips selected randomly.")
    parser.add_argument("-wd", "--working-directory", default=DEFAULT_WORKING_DIRECTORY, type=str, help="The working directory where to look for input files and store output files.")
    parser.add_argument("-i", "--input-file", type=str, default=DEFAULT_INPUT_FILE, help="SUMO rou.xml input file path.")
    parser.add_argument("-p", "--percentages", type=float, nargs="+", default=DEFAULT_PERCENTAGES, help="List of EV percenetages e.g. (0.05, 0.10, 0.20).")
    parser.add_argument("-n", "--num-files", type=int, default=DEFAULT_NUM_FILES, help="Number of files to be generated for each percentage")
    parser.add_argument("-b", "--battery-capacity", type=int, default=DEFAULT_BATTERY_CAPACITY, help="Total Battery Capacity of the Electric Vehicles")

    args = parser.parse_args()

    ev_definer:EVDefiner = EVDefiner()
    
    # Running the script for each percentage num_file times.
    for p in args.percentages:
        for i in range(args.num_files):
            output_file:str = f"{args.working_directory}/routes_{(p * 100):.0f}_{i}.rou.xml"
            ev_definer.define(f"{args.working_directory}/{args.input_file}", output_file, p, args.battery_capacity)
            print(f"File \"{output_file}\" generated.")