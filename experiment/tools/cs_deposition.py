"""
tools/cs_deposition.py
-------------

...
"""

# Internals
from domain.types import LS_Methods, LaneData
from domain.exceptions import InterpreterException
from params import VEHICLES_LENGTH, MAX_STATIONS, DEFAULT_CS


class Interpreter():
    def __init__(self, log_filename : str = "", output_filename : str = "./out.add.xml", max_stations: int = MAX_STATIONS):
        self.log_filename       : str = log_filename
        self.output_filename    : str = output_filename
        self.max_stations       : int = max_stations

        self.lane_visits    : dict[str, LaneData] = {}
        self.selected_lanes : list[LaneData] = []

    def __call__(self, log_filename : str = "", output_filename : str = "", method : LS_Methods = LS_Methods.RANDOM):
        if log_filename:
            self.log_filename = log_filename
        if output_filename:
            self.output_filename = output_filename

        self.__select_lanes(method)
        self.__write_additionals()


    def __get_lane_visits(self) -> None:
        base_filename : str = self.log_filename.split(".")[0]

        with open(f"{base_filename}_lv.csv", "r") as lv_log_file:
            for line in lv_log_file.readlines():
                line = line.strip().split(", ")
                self.lane_visits[line[0]] = LaneData(line[0], float(line[1]), int(line[2]))


    def __select_lanes(self, method: LS_Methods = LS_Methods.RANDOM) -> None:
        self.__get_lane_visits()

        match method:
            case LS_Methods.RANDOM:
                print("Method: RANDOM")
                self.method_random()

            case LS_Methods.GREEDY:
                print("Method: GREEDY")
                self.method_greedy()

            case LS_Methods.OTHER:
                print("Method: OTHER")
                self.method_other()

            case _:
                raise InterpreterException("Invalid Lane Selection Method.")
        
        if self.selected_lanes:
            print(f"selected_lanes: {self.selected_lanes}")


    def __write_additionals(self):
        """ Writes a new station for each of the given lanes in the specified .add.xml filename. """

        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        root = ET.Element("additional")

        for lane in self.selected_lanes:
            lane_length : float = lane.lane_length
            start_pos : int = lane_length / 2 - DEFAULT_CS.length / 2

            parking_area = ET.SubElement(root, "parkingArea")
            parking_area.set("id",              f"pa_{lane.lane_id}")
            parking_area.set("lane",            lane.lane_id)
            parking_area.set("startPos",        str(start_pos))
            parking_area.set("endPos",          str(start_pos + DEFAULT_CS.length))
            parking_area.set("roadsideCapacity", str(DEFAULT_CS.capacity))
            parking_area.set("friendlyPos",     "true") # Whether Parking Area's postions should automatically be corrected.
            parking_area.set("angle",           "90")

            charging_station = ET.SubElement(root, "chargingStation")
            charging_station.set("id",          f"cs_{lane.lane_id}") # Simulation definition: ID = [<id>:<capacity>]
            charging_station.set("power",       str(DEFAULT_CS.power))
            charging_station.set("efficiency",  str(DEFAULT_CS.efficiency))
            charging_station.set("lane",        lane.lane_id)
            charging_station.set("startPos",    str(start_pos))
            charging_station.set("endPos",      str(start_pos + DEFAULT_CS.length))
            charging_station.set("chargeDelay", str(DEFAULT_CS.charge_delay))
            charging_station.set("friendlyPos", "true") # Whether Charging Station's postions should automatically be corrected.
            # charging_station.set("pos", "10.00")

        #tree = ET.ElementTree(root)
        pretty_xml_str = minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent="   ") # In order to have indentation

        with open(self.output_filename, "w", encoding="UTF-8") as file:
            file.write(pretty_xml_str)

        #tree.write(output_filename, xml_declaration=True, encoding="UTF-8")



    def method_random(self) -> list[str]:
        """ Selects random lanes from the ones visited based on the maximum vehicles per station (capacity). """
        from random import sample

        cadidate_lanes : list[LaneData] = [lane for lane in self.lane_visits.values() if lane.lane_length >= DEFAULT_CS.length]
        self.selected_lanes = sample(list(cadidate_lanes), self.max_stations)


    def method_greedy(self):
        """ Selects only the lanes with the greatest number of visits """

        # Sorting the lane visits dictionary by the visits count in decreasing order
        sorted_lanes: list[LaneData] = list(sorted(self.lane_visits.values(), key= lambda lane: lane.visits_count, reverse=True))

        candidate_lanes : list[LaneData] = [lane for lane in sorted_lanes if lane.lane_length >= DEFAULT_CS.length]
        self.selected_lanes = candidate_lanes[0 : self.max_stations]


    def method_other(self):
        ...



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Uses Simulation's logged infromation for selecting lanes to install Charging Stations." \
        " The corresponding .add.xml file is generated with the charging stations.")
    parser.add_argument("-i", "--input-file", type=str, default="./data/simulation.log", help="Simulation's log data file.")
    parser.add_argument("-o", "--output-file", type=str, default="./out.add.xml", help="SUMO's .add.xml output file name.")
    parser.add_argument("-ms", "--max-stations", type=int, default=10, help="Maximum number of stations to be added.")
    parser.add_argument("-m", "--method", type=int, default=LS_Methods.RANDOM, help="Lane Selection Method: \n"\
                        "\tAvaliable Methods: [RANDOM = 0, GREEDY = 1, ...]")

    args = parser.parse_args()

    interpreter: Interpreter = Interpreter(max_stations=args.max_stations)
    interpreter(log_filename=args.input_file, output_filename=args.output_file, method=LS_Methods(args.method))