import xml.etree.ElementTree as ET
import random
import argparse


class EVDefiner:
    def __init__(self):
        pass
        
    def _add_vtypes(self, root:ET.Element, battery_capacity:int) -> None:
        """ Checks if vTypes for Normal and Electric vehicles are defined. Defines it if not. """

        if root.find("vType[@id=\"normal_vehicle\"]") == None:
            vtype_normal = ET.Element(
                "vType", attrib={
                    "id": "normal_vehicle",
                    "length": "5",
                    "accel": "2.6",
                    "decel": "4.5",
                    "sigma": "0.5",
                    "maxSpeed": "50",
                    "color": "1,1,0"
                }
            )
            root.insert(0, vtype_normal)
            
        if root.find("vType[@id=\"electric_vehicle\"]") == None:
            ev_attributes = {
                "id": "electric_vehicle",
                "length": "5",
                "accel": "2.6",
                "decel": "4.5",
                "sigma": "0.5",
                "maxSpeed": "50",
                "mass": "1036.00",
                "color": "0,1,0",
                "emissionClass": "Energy/default"
            }

            # soulEV65 parameters
            ev_params = {
                "has.battery.device": "true",
                "device.battery.capacity": f"{battery_capacity}",   # Battery capacity [Wh]
                "maximumPower": "150000",
                "device.battery.maximumChargeRate": "150000",
                "airDragCoefficient": "0.35",
                "constantPowerIntake": "100",
                "frontSurfaceArea": "2.6",
                "propulsionEfficiency": "0.98",
                "radialDragCoefficient": "0.1",
                "recuperationEfficiency": "0.96",                   # High value, change it if necessary.
                "rollDragCoefficient": "0.01",                      # How much resistance a rolling object experiences.
                "stoppingThreshold": "0.1",
                "rotatingMass": "40"
            }

            vtype_electric = ET.Element("vType", ev_attributes)
            for key, value in ev_params.items():
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
    parser.add_argument("-r", "--reference-path", type=str, default=".", help="Reference foulder to look for files.")
    parser.add_argument("-i", "--input-file", type=str, default="routes.rou.xml", help="SUMO rou.xml input file path.")
    parser.add_argument("-p", "--percentages", type=float, nargs="+", default=[0.05, 0.10, 0.20], help="List of EV percenetages e.g. (0.05, 0.10, 0.20).")
    parser.add_argument("-n", "--num-files", type=int, default=5, help="Number of file to be generated for each percentage")
    parser.add_argument("-b", "--battery-capacity", type=int, default=64000, help="Total Battery Capacity of the Electric Vehicles")

    args = parser.parse_args()

    ev_definer:EVDefiner = EVDefiner()
    
    # Running the script for each percentage num_file times.
    for p in args.percentages:
        for i in range(args.num_files):
            output_file:str = f"{args.reference_path}/routes_{(p * 100):.0f}_{i}.rou.xml"
            ev_definer.define(f"{args.reference_path}/{args.input_file}", output_file, p, args.battery_capacity)
            print(f"File \"{output_file}\" generated.")