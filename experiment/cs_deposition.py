from charging_station import ChargingStation as CS
from sim_tools import LaneData, VEHICLES_LENGTH

from enum import Enum



MAX_STATIONS: int = 10

# ===< Lane Selection Methods >===
class LS_Methods(Enum):
    RANDOM = 0
    GREEDY = 1
    OTHER = 2

class Interpreter():
    def __init__(self, log_filename: str = "", output_filename: str = "", max_stations: int = MAX_STATIONS):
        self.log_filename: str = log_filename
        self.output_filename: str = output_filename
        self.max_stations: int = max_stations
        self.lane_visits: dict[str, LaneData] = {}
        self.selected_lanes: list[LaneData] = []

    def __get_lane_visits(self) -> None:
        base_filename: str = self.log_filename.split(".")[0]

        with open(f"{base_filename}_lv.csv", "r") as lv_log_file:
            for line in lv_log_file.readlines():
                line = line.strip().split(", ")
                self.lane_visits[line[0]] = LaneData(line[0], float(line[1]), int(line[2]))


    def method_random(self) -> list[str]:
        """ Selects random lanes from the ones visited bases on the maximum """
        from random import sample

        cadidate_lanes: list[LaneData] = [lane for lane in self.lane_visits.values() if lane.lane_length >= 2 * VEHICLES_LENGTH]
        self.selected_lanes = sample(list(cadidate_lanes), self.max_stations)

    def method_greedy(self):
        """ Selects only the lanes with the greatest number of visits """

        # Sorting the lane visits dictionary by the visits count in decreasing order
        sorted_lanes: list[LaneData] = list(sorted(self.lane_visits.values(), key= lambda lane: lane.visits_count, reverse=True))

        self.selected_lanes = sorted_lanes[0:self.max_stations]


    def method_other(self):
        ...

    def select_lanes(self, method: LS_Methods = LS_Methods.RANDOM) -> None:
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
                print("[Interpreter.select_lanes] ERROR: Invalid Lane Selection Method.")
        
        if self.selected_lanes:
            print(f"selected_lanes: {self.selected_lanes}")

    def write_additionals(self):
        CS.write_additional_file(self.selected_lanes, self.output_filename)

    def __call__(self, log_filename: str = "", output_filename:str = "./out.add.xml", method: LS_Methods = LS_Methods.RANDOM):
        if log_filename:
            self.log_filename = log_filename
        self.output_filename = output_filename

        self.select_lanes(method)
        self.write_additionals()


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