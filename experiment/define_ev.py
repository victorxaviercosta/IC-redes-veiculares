import xml.etree.ElementTree as ET
import random
import argparse


class EVDefiner:
    def __init__(self):
        pass
        
    def _add_vtypes(self, root:ET.Element) -> None:
        """
        Checks if vTypes for Normal and Electric vehicles are defined. Defines it if not.
        """

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
            vtype_electric = ET.Element(
                "vType", attrib={
                    "id": "electric_vehicle",
                    "length": "5",
                    "accel": "2.6",
                    "decel": "4.5",
                    "sigma": "0.5",
                    "maxSpeed": "50",
                    "color": "1,1,0"
                }
            )
            # soulEV65 parameters
            vtype_electric.append(ET.Element("param", attrib={"key": "has.battery.device", "value": "true"}))
            vtype_electric.append(ET.Element("param", attrib={"key": "device.battery.capacity", "value": "64000"})) # Battery capacity [Wh]
            vtype_electric.append(ET.Element("param", attrib={"key": "airDragCoefficient", "value": "0.35"}))
            vtype_electric.append(ET.Element("param", attrib={"key": "constantPowerIntake", "value": "100"}))
            vtype_electric.append(ET.Element("param", attrib={"key": "frontSurfaceArea", "value": "2.6"}))
            vtype_electric.append(ET.Element("param", attrib={"key": "internalMomentOfInertia", "value": "40"})) # Replacing with rotatingMass
            vtype_electric.append(ET.Element("param", attrib={"key": "maximumPower", "value": "150000"}))
            vtype_electric.append(ET.Element("param", attrib={"key": "propulsionEfficiency", "value": ".98"}))
            vtype_electric.append(ET.Element("param", attrib={"key": "radialDragCoefficient", "value": "0.1"}))
            vtype_electric.append(ET.Element("param", attrib={"key": "recuperationEfficiency", "value": ".96"})) # High value, change it if necessary.
            vtype_electric.append(ET.Element("param", attrib={"key": "rollDragCoefficient", "value": "0.01"})) # How much resistance a rolling object experiences.
            vtype_electric.append(ET.Element("param", attrib={"key": "stoppingThreshold", "value": "0.1"}))
            vtype_electric.append(ET.Element("param", attrib={"key": "mass", "value": "1830"}))
            root.insert(0, vtype_electric)

    def define(self, input_file:str, output_file:str, ev_percentage:float) -> None:
        """
        Modifies a route file to define a percentage of the trips as ev trips selected randomly.
        """

        tree: ET.ElementTree[ET.Element[str]] = ET.parse(input_file)
        root: ET.Element[str] = tree.getroot()

        self._add_vtypes(root)

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

    args = parser.parse_args()

    definer:EVDefiner = EVDefiner()
    
    # Running the script for each percentage num_file times.
    for p in args.percentages:
        for i in range(args.num_files):
            output_file:str = f"{args.reference_path}/routes_{(p * 100):.0f}_{i}.rou.xml"
            definer.define(f"{args.reference_path}/{args.input_file}", output_file, p)
            print(f"File \"{output_file}\" generated.")