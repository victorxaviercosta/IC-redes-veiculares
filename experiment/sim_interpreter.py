from enum import Enum

from charging_station import ChargingStation as CS


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
        self.lane_visits: dict[str, list[float, int]] = {}
        self.selected_lanes: list[tuple[str, float]] = []

    def __get_lane_visits(self) -> None:
        in_lv_section: bool = False
        with open(self.log_filename, "r") as sim_log_file:
            for line in sim_log_file.readlines():
                if line == "End Lane Visits\n":
                    break

                if in_lv_section:
                    line = line.strip().split(", ")
                    lane_id: str = line[0]
                    lane_lenght: float = float(line[1])
                    visits_count: int = int(line[2])
                    self.lane_visits[lane_id] = [lane_lenght, visits_count]
                
                elif "Lane Visits:" in line:
                    in_lv_section = True


    def method_random(self) -> list[str]:
        """ Selects random lanes from the ones visited bases on the maximum """
        from random import sample

        # Converting lanes dictionary into a list of tuples (<lane_id>, <length>)
        lanes: list[tuple[str, float]] = [(lane_id, self.lane_visits[lane_id][0]) for lane_id in self.lane_visits]
        self.selected_lanes = sample(lanes, self.max_stations)
        print(f"selected_lanes: {self.selected_lanes}")

    def method_greedy(self):
        """ Selects only the lanes with the greatest number of visits """

        # Sorting the lane visits dictionary by the visits count in decreasing order
        sorted_lanes: dict[tuple[float, int]] = dict(sorted(self.lane_visits.items(), key= lambda x: x[1][1], reverse=True))

        # Converting lanes dictionary into a list of tuples (<lane_id>, <length>)
        lanes: list[tuple[str, float]] = [(lane_id, sorted_lanes[lane_id][0]) for lane_id in sorted_lanes]
        self.selected_lanes = lanes[0:self.max_stations]
        print(f"selected_lanes: {self.selected_lanes}")


    def method_other(self):
        ...

    def select_lanes(self, method: LS_Methods = LS_Methods.RANDOM) -> None:
        self.__get_lane_visits()

        match method:
            case LS_Methods.RANDOM:
                print("RANDOM")
                self.method_random()

            case LS_Methods.GREEDY:
                print("GREEDY")
                self.method_greedy()

            case LS_Methods.OTHER:
                print('OTHER')
                self.method_other()

            case _:
                print("[Interpreter.select_lanes] ERROR: Invalid Lane Selection Method.")

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