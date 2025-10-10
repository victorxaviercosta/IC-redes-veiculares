from sim_tools import LaneData

from dataclasses import dataclass
import xml.etree.ElementTree as ET

@dataclass(frozen = True)
class ChargingStation():
    """ A class defining a Charging Station and utility methods. """
    """ Capacity is not supported in SUMO by default do it's here simulated by setting the length of the
        charging station accordingly to the fixed size of a vehicle. """

    power: float        # [W]
    efficiency: float   # [0,1]
    capacity: int       # [u] (units, maximum number of vehicles that can charge simultaniosly)
    charge_delay: float # [s] (measured in Simulation's step-length, 1 second by default)
    length: float       # [m]

    @staticmethod
    def write_additional_file(lanes: list[LaneData], output_filename: str) -> None:
        """ Writes a new station for each of the given lanes in the specified .add.xml filename. """

        from xml.dom import minidom
        root = ET.Element("additional")

        for lane in lanes:
            lane_length: float = lane.lane_length
            charging_station = ET.SubElement(root, "chargingStation")
            charging_station.set("id",          f"cs_{lane.lane_id}:{DEFAULT_CS.capacity}") # Simulation definition: ID = [<id>:<capacity>]
            charging_station.set("power",       str(DEFAULT_CS.power))
            charging_station.set("efficiency",  str(DEFAULT_CS.efficiency))
            charging_station.set("lane",        lane.lane_id)
            charging_station.set("startPos",    str(lane_length / 2))
            charging_station.set("endPos",      str(lane_length / 2 + (DEFAULT_CS.length * DEFAULT_CS.capacity)))
            charging_station.set("chargeDelay", str(DEFAULT_CS.charge_delay))
            charging_station.set("friendlyPos", "true") # Whether Charging Station's postions should automatically be corrected.
            # charging_station.set("pos", "10.00")

        #tree = ET.ElementTree(root)
        pretty_xml_str = minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent="   ") # In order to have indentation

        with open(output_filename, "w", encoding="UTF-8") as file:
            file.write(pretty_xml_str)

        #tree.write(output_filename, xml_declaration=True, encoding="UTF-8")

    @staticmethod
    def getCapacity(cs_id: str) -> int:
        """ Assuming Simulation's definitions that charging station's capacity is incorporated in it's ID in the format: [<id>:<capacity>] """
        try:
            return int( cs_id.split(":")[-1] )
        except:
            return 0


""" Default Charging Station Used to be added at the Simulation """
DEFAULT_CS: ChargingStation = ChargingStation( 
    power = 22_000,
    efficiency = 0.95,
    capacity = 2,
    charge_delay = 5,
    length = 5
)
