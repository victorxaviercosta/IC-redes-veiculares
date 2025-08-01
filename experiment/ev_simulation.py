"""
Refs: https://sumo.dlr.de/docs/Models/Electric.html#tracking_fuel_consumption_for_non-electrical_vehicles
"""

from sim_logging import LogParameters as Log
from simulation import Simulation
from charging_station import ChargingStation as CS
import sim_tools as tools

import traci
import traci.constants
import traci.exceptions

from typing import override
from typing import Any
import xml.etree.ElementTree as ET

# ===< Simulation's constant parameters >===
EV_MAX_BATTERY_CAPACITY: float = 30000  # [Wh]
INTIAL_BATTERY_PERCENTAGE: float = 0.3  # [0,1]
LOW_BATTERY_PERCENTAGE: float = 0.25    # [0,1]
MAX_CHARGING_STOP_DURATION: int = 1800  # [s]
MAX_VEHICLE_WAITING_TIME: int = 15      # [s]
RANDOM_BATTERY_START: bool = False

ELECTRIC_VEHICLE_VTYPE: str = "electric_vehicle"
PAR_CHARGE_LEVEL: str = "device.battery.chargeLevel"


class EV_Simulation(Simulation):
    def __init__(self, 
                 config_file: str, add_files: str = "", 
                 tripifo_out_file: str = "", log_file: str = "./data/sumo.log", 
                 delay: int = 0, 
                 gui: bool = False, 
                 gui_settings_files: str = "", 
                 auto_start: bool = False, 
                 verbose: bool = False,
                 end_time: int = 3600,
                 sim_log_filename: str = "data/simulation.log"):
        super().__init__(config_file, add_files, tripifo_out_file, log_file, delay, gui, gui_settings_files, auto_start, verbose, end_time, sim_log_filename)
        self.veh_states: dict[str, dict[str, Any]] = {}     # { veh_ID: { "origin": "<edge_ID>", "destiny": "<edge_ID>", "lowBatteryStart": <start_time> } }
        self.reroutes: list[tuple[str, str, str]] = []      # [ (veh_ID, original_destiny, new_destiny) ]
        self.lane_visits: dict[str, list[float, int]] = {} # { "Lane_ID": [<lane_lenght:float>, <visits_count: int>] }
        # self.flag_avaliable_stations: bool = False      # Indicates whether there's at least one station avaliable in the network.

    @override
    def pre_start(self) -> None:
        """ Here's defined the logics to be executed before the first step of the simulation. """
        ...

    @override
    def step(self) -> None:
        """ Here is defined the logic to be executed at each simulation step """

        for veh_ID in traci.vehicle.getIDList(): # For each vehicle currently in the network
            if traci.vehicle.getTypeID(veh_ID) == ELECTRIC_VEHICLE_VTYPE:
                veh_route: tuple[str] = traci.vehicle.getRoute(veh_ID)

                # At the first Check initializates the origin and destination of the vehicle.
                if veh_ID not in self.veh_states:   # TODO: (no urgency) Look for a better way of making this initialization.
                    self.veh_states[veh_ID] = {}
                    self.veh_states[veh_ID]["origin"] = veh_route[0]
                    self.veh_states[veh_ID]["destiny"] = veh_route[-1]
                    self.veh_states[veh_ID]["lowBatteryStart"] = 0.0

                    from random import random
                    if RANDOM_BATTERY_START:
                        tools.set_charge_level(veh_ID, EV_MAX_BATTERY_CAPACITY * max(0.25, random()))
                    else:
                        tools.set_charge_level(veh_ID, EV_MAX_BATTERY_CAPACITY * INTIAL_BATTERY_PERCENTAGE)
                    
                    self.log_charge_level(veh_ID)

                
                # Checking if the vehicle is waiting for too much time (to prevent blocking the road)
                if traci.vehicle.getWaitingTime(veh_ID) >= MAX_VEHICLE_WAITING_TIME:
                    self.log(f"Vehicle {veh_ID} waited {MAX_VEHICLE_WAITING_TIME} seconds at it's stop. Canceling.", level=Log.ESSENTIALS)
                    traci.vehicle.replaceStop(veh_ID, 0, "")    # Removing vehicle's stop.

                handle_low_battery:bool = True

                # If the vehicle is currently parked there's no need to handle low battery.
                if traci.vehicle.getStopState(veh_ID) >= 2:
                    handle_low_battery = False

                # Checking if vehicle have been previously rerouted:
                for rr in self.reroutes:
                    if (rr[0] == veh_ID):
                        handle_low_battery = False # No need to handle battery level since it was already resolved.

                        # If the vehicle is stopped at it's current destiny.
                        if(traci.vehicle.getSpeed(veh_ID) == 0 and rr[-1] == traci.vehicle.getRoadID(veh_ID)):
                            traci.vehicle.changeTarget(veh_ID, rr[1])
                            self.reroutes.remove(rr)
                            self.log(f"Vehicle {veh_ID} route reestablished: \tFrom: {rr[-1]} - To: {rr[1]}", level=Log.UTILS)
                            #print(f"{traci.vehicle.getRoute(veh_ID)}")

                            # Checking if the vehicle is currently parked.
                            if traci.vehicle.getStopState(veh_ID) >= 2:
                                low_battery_delta_time: float = traci.simulation.getTime() - self.veh_states[veh_ID]["lowBatteryStart"]
                                self.log(f"Vehicle {veh_ID} wait time with low battery: {low_battery_delta_time} [s]", level=Log.ESSENTIALS)
                                self.veh_states[veh_ID]["lowBatteryStart"] = 0.0

                if handle_low_battery:
                    self.check_destiny_reached(veh_ID)

                self.log_charge_level(veh_ID, Log.LOG_BATTERY_PERIOD)

                self.check_charge_level(veh_ID, handle_low_battery)

                self.update_lane_visits(veh_ID)


    @override
    def post_end(self) -> None:
        """ Here's defined the logics to be executed after the last step of the simulation. """
        
        for veh_ID in traci.vehicle.getIDList(): # For each vehicle currently in the network
            if traci.vehicle.getTypeID(veh_ID) == ELECTRIC_VEHICLE_VTYPE:
                self.log_charge_level(veh_ID, needed=True)



    @override
    def write_log(self) -> None:
        self.log_lane_visits()
        ...



    def check_charge_level(self, veh_ID: str, handle_low_battery: bool) -> None:
        """ Check's for the given vehicle's battery charge level handling low battery if requested """

        battery_charge: float = tools.get_charge_level(veh_ID)
        veh_position: tuple[float, float] = traci.vehicle.getPosition(veh_ID)

        tools.change_vehicle_color(veh_ID, battery_charge, EV_MAX_BATTERY_CAPACITY)

        # If vehicle have low battery:
        if handle_low_battery and (battery_charge <= (EV_MAX_BATTERY_CAPACITY * LOW_BATTERY_PERCENTAGE)):
            firstTimeLowBattery: bool = self.veh_states[veh_ID]["lowBatteryStart"] == 0
            if firstTimeLowBattery:
                self.log(f"{veh_ID} Low Battery: {battery_charge} Wh", level=Log.ESSENTIALS)

            closest_station = self.search_nearest_station(veh_position)

            # if there is any nearest station:
            if closest_station:
                self.reroute_vehicle(veh_ID, closest_station)
                self.log(f"Found closest station for {veh_ID}: {closest_station}", level=Log.ESSENTIALS)
                #self.log(f"rereoutes: {self.reroutes}")


            elif firstTimeLowBattery:
                self.log(f"No Station avaliable for {veh_ID}", level=Log.ESSENTIALS)
            
            # Registring the vehicle's start time with low battery.
            if firstTimeLowBattery:
                self.veh_states[veh_ID]["lowBatteryStart"] = traci.simulation.getTime()


    def search_nearest_station(self, veh_pos: tuple[float]) -> str:
        """ Searches for the nearest station from the given vehicle position (For now it only considers euclidian distance). """
        self.log(f"Searching Nearest Station", level=Log.SPECIFICS)

        closest_station:str = ""
        min_distance: float = float("inf")

        for cs_ID in traci.chargingstation.getIDList():
            # If vehicle's maximum capacity was reached yet, skip it.
            if (traci.chargingstation.getVehicleCount(cs_ID) == CS.getCapacity(cs_ID)):
                continue          

            station_position: tuple[float, float] = tools.get_station_postion(cs_ID)

            # Calculating euclidian distance between the vehicle and the lane.
            distance:float = ((veh_pos[0] - station_position[0])**2 + (veh_pos[1] - station_position[1])**2)**0.5

            if Log.LOG_STATION_DISTANCES:
                self.log(f"\t{cs_ID} - distance: {distance} - position: {station_position}")

            if (distance < min_distance) :
                min_distance = distance
                closest_station = cs_ID
            
        return closest_station
    

    def reroute_vehicle(self, veh_ID: str, closest_station: str) -> None:
        """ Set's a new route to the closest_station for the given vehicle """

        original_route: tuple[str] = traci.vehicle.getRoute(veh_ID)
        original_destiny: str = original_route[-1] if original_route else None

        station_lane_ID: str = traci.chargingstation.getLaneID(closest_station)

        try:
            # Changing vehicle destiny to the closest_station's edge.
            new_destiny: str = station_lane_ID.split('_')[0]
            if(new_destiny == traci.vehicle.getLaneID(veh_ID).split('_')[0]):
                self.log(f"Closest_station is back in {veh_ID}'s lane. Skiping.", level=Log.ESSENTIALS)
                return

            traci.vehicle.changeTarget(veh_ID, new_destiny)

            battery_needed = EV_MAX_BATTERY_CAPACITY - tools.get_charge_level(veh_ID)
            duration: int = min( MAX_CHARGING_STOP_DURATION,
                                 battery_needed / traci.chargingstation.getChargingPower(closest_station) * 3600 )

            # Adding a charging stop at the closest_station for [duration] seconds.
            traci.vehicle.setChargingStationStop(veh_ID, closest_station, duration=duration, flags=traci.constants.STOP_PARKING)
            #traci.vehicle.setStopParameter(veh_ID, 0, "parking", "true") # This way, the vehicles park to use the charging station (beside the lane).
        
        except traci.exceptions.TraCIException as excp:
            self.log(f"Error while seting Station stop for vehicle {veh_ID}: \n\t[Exception] {excp}", level=Log.ESSENTIALS)
            return

        # Add's the vehicle to the list of rerouted vehicles
        self.reroutes.append((veh_ID, original_destiny, new_destiny))

        self.log(f"Vehicle {veh_ID} rerouted to {closest_station} for {duration} seconds:", level=Log.ESSENTIALS)
        self.log(f"OriginalDes: {original_destiny} - NewDest: {new_destiny}", level=Log.UTILS)


    def check_destiny_reached(self, veh_ID:str):
        """ Checks if the vehicle reched it's destiny and reroutes it to it's previous origin (making the vehicle cicle across it's route). """

        veh_edge: str = traci.vehicle.getRoadID(veh_ID)
        
        if veh_edge == self.veh_states[veh_ID]["destiny"]:
            if Log.LOG_END_OF_ROUTE_REROUTE:
                self.log(f"Rerouting {veh_ID} from {self.veh_states[veh_ID]["destiny"]} to {self.veh_states[veh_ID]["origin"]} ({veh_edge})")

            # Swaps orign and destiny
            self.veh_states[veh_ID]["origin"], self.veh_states[veh_ID]["destiny"] = (self.veh_states[veh_ID]["destiny"], self.veh_states[veh_ID]["origin"])
            new_route: tuple[str] = traci.simulation.findRoute(veh_edge, self.veh_states[veh_ID]["destiny"]).edges
            traci.vehicle.setRoute(veh_ID, new_route)

    
    def update_lane_visits(self, veh_ID:str) -> None:
        """ Get's the given vehicle's current lane and updates the lane visits counter for that lane """

        lane_ID: str = traci.vehicle.getLaneID(veh_ID)
        if lane_ID and lane_ID[0] != ":":
            if lane_ID not in self.lane_visits:
                self.lane_visits[lane_ID] = [traci.lane.getLength(lane_ID), 0]
            self.lane_visits[lane_ID][1] += 1



    # ===< Logging Methods >====

    def log_charge_level(self, veh_ID:str, interval: int = 1, needed: bool = False) -> None:
        """ Periodically log's the given vehicle battery level with timestamp """
        if needed or (Log.LOG_CHARGE_LEVEL and (traci.simulation.getTime() % interval == 0)):
            self.log(f"Vehicle {veh_ID} charge_level = {traci.vehicle.getParameter(veh_ID, PAR_CHARGE_LEVEL)} Wh")


    def log_lane_visits(self) -> None:
        """ Writes the visists count for each lane in the Simulation's log file. """
        try:
            self.logging.write(f"\nLane Visits: <ID>, <length>, <count>\n")
            for lane in self.lane_visits:
                self.logging.write(f"{lane}, {self.lane_visits[lane][0]}, {self.lane_visits[lane][1]}\n")
            self.logging.write(f"End Lane Visits\n")
        except IOError as error:
            print(error)


if __name__ == "__main__":
    simulation = EV_Simulation(
        config_file="ev_test/ev_test.sumocfg",
        delay=30,
        gui=True,
        verbose=True,
        end_time=20_000
    )

    simulation.start()