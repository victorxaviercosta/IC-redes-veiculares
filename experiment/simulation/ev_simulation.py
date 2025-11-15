"""
simulation/simulation.py
-------------

...

Refs: https://sumo.dlr.de/docs/Models/Electric.html#tracking_fuel_consumption_for_non-electrical_vehicles
"""

# Internals
from domain.types import VehState, Reroute, LaneData, ChargingStation
from domain.types import Volume as Vol
from .simulation import Simulation

from utils.sumo_setup import TraciParameters
import utils.traci_utils as util

from params import (
    EV_MAX_BATTERY_CAPACITY,
    LOW_BATTERY_PERCENTAGE,
    INTIAL_BATTERY_PERCENTAGE,
    RANDOM_BATTERY_START,

    MAX_CHARGING_STOP_DURATION,
    MAX_VEHICLE_WAITING_TIME,

    CIRCLE_ROUTE,

    ELECTRIC_VEHICLE_VTYPE,
)

from params import (
    LOG_CHARGE_PERIOD,
    LOG_CHARGE_LEVEL,
    LOG_STATION_DISTANCES,
    LOG_END_OF_ROUTE_REROUTE
)

# Traci
import traci
import traci.constants
import traci.exceptions

# Python
from typing import override, Any


class EV_Simulation(Simulation):
    def __init__(self, params: TraciParameters, sim_log_filename: str = "data/simulation.log"):
        params.sumo_log_file = "./data/sumo.log"

        super().__init__(params, sim_log_filename)
        self.veh_states: dict[str, VehState] = {} # Stores information of the current state of each vehicle in the simulation.
        self.reroutes:   dict[str, Reroute]  = {} # Stores the information for each reroute currently applied to a vehicle.
        self.lane_data:  dict[str, LaneData] = {} # Stores data for all lanes that had been visited on the simulation.

    @override
    def pre_start(self) -> None:
        """ Here's defined the logics to be executed before the first step of the simulation. """
        ...

    @override
    def step(self) -> None:
        """ Here is defined the logic to be executed at each simulation step """
        from random import random

        for veh_ID in traci.vehicle.getIDList(): # For each vehicle currently in the network
            if traci.vehicle.getTypeID(veh_ID) == ELECTRIC_VEHICLE_VTYPE:
                veh_route: tuple[str] = traci.vehicle.getRoute(veh_ID)

                # At the first Check initializates the origin and destination of the vehicle.
                if veh_ID not in self.veh_states:   
                    self.veh_states[veh_ID] = VehState(veh_route[0], veh_route[-1], 0.0)

                    if RANDOM_BATTERY_START:
                        util.set_charge_level(veh_ID, EV_MAX_BATTERY_CAPACITY * max(0.25, random()))
                    else:
                        util.set_charge_level(veh_ID, EV_MAX_BATTERY_CAPACITY * INTIAL_BATTERY_PERCENTAGE)
                    
                    self.log_charge_level(veh_ID)

                
                # Checking if the vehicle is waiting for too much time for a CS (to prevent blocking the road)
                self.check_cs_stop(veh_ID)

                handle_low_battery: bool = True
                # If the vehicle is currently parked there's no need to handle low battery.
                if traci.vehicle.getStopState(veh_ID) >= 2:
                    handle_low_battery = False

                # Checking if vehicle have been previously rerouted:
                if veh_ID in self.reroutes:
                    rr = self.reroutes[veh_ID]
                    handle_low_battery = False # No need to handle battery level since it was already resolved.

                    # If the vehicle is stopped at it's current destiny.
                    if(traci.vehicle.getSpeed(veh_ID) == 0 and rr.new_destiny == traci.vehicle.getRoadID(veh_ID)):
                        traci.vehicle.changeTarget(veh_ID, rr.original_destiny)
                        self.log(f"Vehicle {veh_ID} route reestablished: \tFrom: {rr.new_destiny} - To: {rr.original_destiny}", level=Vol.UTILS)
                        del self.reroutes[veh_ID]
                        #print(f"{traci.vehicle.getRoute(veh_ID)}")

                        # Checking if the vehicle is currently parked.
                        if traci.vehicle.getStopState(veh_ID) >= 2:
                            low_battery_delta_time: float = traci.simulation.getTime() - self.veh_states[veh_ID].low_battery_start
                            self.log(f"Vehicle {veh_ID} wait time with low battery: {low_battery_delta_time} [s]", level=Vol.ESSENTIALS)
                            self.veh_states[veh_ID].low_battery_start = 0.0

                if CIRCLE_ROUTE and handle_low_battery:
                    self.circle_vehicle_route(veh_ID)

                self.log_charge_level(veh_ID, LOG_CHARGE_PERIOD)

                self.handle_charge_level(veh_ID, handle_low_battery)

                self.update_lane_visits(veh_ID)


    @override
    def post_end(self) -> None:
        """ Here's defined the logics to be executed after the last step of the simulation. """
        
        self.log(f"Last charge level log: ")
        for veh_ID in traci.vehicle.getIDList(): # For each vehicle currently in the network
            if traci.vehicle.getTypeID(veh_ID) == ELECTRIC_VEHICLE_VTYPE:
                self.log_charge_level(veh_ID, needed=True)



    @override
    def write_log(self) -> None:
        self.log_lane_visits()
        ...



    def handle_charge_level(self, veh_ID: str, handle_low_battery: bool) -> None:
        """ Check's for the given vehicle's battery charge level handling low battery if requested """

        battery_charge: float = util.get_charge_level(veh_ID)
        veh_position: tuple[float, float] = traci.vehicle.getPosition(veh_ID)

        util.change_vehicle_color(veh_ID, battery_charge, EV_MAX_BATTERY_CAPACITY)

        # If vehicle have low battery:
        if handle_low_battery and (battery_charge <= (EV_MAX_BATTERY_CAPACITY * LOW_BATTERY_PERCENTAGE)):
            firstTimeLowBattery: bool = self.veh_states[veh_ID].low_battery_start == 0
            if firstTimeLowBattery:
                self.log(f"{veh_ID} Low Battery: {battery_charge} Wh", level=Vol.ESSENTIALS)

            closest_station = self.search_nearest_station(veh_position)

            # if there is any nearest station:
            if closest_station:
                self.reroute_vehicle(veh_ID, closest_station)
                self.log(f"Found closest station for {veh_ID}: {closest_station}", level=Vol.ESSENTIALS)
                #self.log(f"rereoutes: {self.reroutes}")


            elif firstTimeLowBattery:
                self.log(f"No Station avaliable for {veh_ID}", level=Vol.ESSENTIALS)
            
            # Registring the vehicle's start time with low battery.
            if firstTimeLowBattery:
                self.veh_states[veh_ID].low_battery_start = traci.simulation.getTime()


    def search_nearest_station(self, veh_pos: tuple[float]) -> str:
        """ Searches for the nearest station from the given vehicle position (For now it only considers euclidian distance). """
        self.log(f"Searching Nearest Station", level=Vol.SPECIFICS)

        closest_station: str = ""
        min_distance: float = float("inf")

        for cs_ID in traci.chargingstation.getIDList():
            # If satations's maximum capacity was reached yet, skip it.
            if (traci.chargingstation.getVehicleCount(cs_ID) == ChargingStation.getCapacity(cs_ID)): # TODO: Could lead to a dead lock aperently !!!!
                continue          

            station_position: tuple[float, float] = util.get_station_postion(cs_ID)

            # Calculating euclidian distance between the vehicle and the lane.
            distance:float = ((veh_pos[0] - station_position[0])**2 + (veh_pos[1] - station_position[1])**2)**0.5

            if LOG_STATION_DISTANCES:
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
                self.log(f"Closest_station is back in {veh_ID}'s lane. Skiping.", level=Vol.ESSENTIALS)
                return

            traci.vehicle.changeTarget(veh_ID, new_destiny)

            battery_needed = EV_MAX_BATTERY_CAPACITY - util.get_charge_level(veh_ID)
            duration: int = min( MAX_CHARGING_STOP_DURATION,
                                 battery_needed / traci.chargingstation.getChargingPower(closest_station) * 3600 )

            # Adding a charging stop at the closest_station for [duration] seconds.
            traci.vehicle.setChargingStationStop(veh_ID, closest_station, duration=duration, flags=traci.constants.STOP_PARKING)
            #traci.vehicle.setStopParameter(veh_ID, 0, "parking", "true") # This way, the vehicles park to use the charging station (beside the lane).
        
        except traci.exceptions.TraCIException as excp:
            self.log(f"Error while seting Station stop for vehicle {veh_ID}: \n\t[Exception] {excp}", level=Vol.ESSENTIALS)
            return

        # Add's the vehicle to the list of rerouted vehicles
        self.reroutes[veh_ID] = Reroute(veh_ID, original_destiny, new_destiny)

        self.log(f"Vehicle {veh_ID} rerouted to {closest_station} for {duration} seconds:", level=Vol.ESSENTIALS)
        self.log(f"OriginalDes: {original_destiny} - NewDest: {new_destiny}", level=Vol.UTILS)


    def circle_vehicle_route(self, veh_ID:str):
        """ Checks if the vehicle reched it's destiny and reroutes it to it's previous origin (making the vehicle cicle across it's route). """

        veh_edge: str = traci.vehicle.getRoadID(veh_ID)
        
        if veh_edge == self.veh_states[veh_ID].destiny:
            if LOG_END_OF_ROUTE_REROUTE:
                self.log(f"Rerouting {veh_ID} from {self.veh_states[veh_ID].destiny} to {self.veh_states[veh_ID].origin} ({veh_edge})")

            # Swaps orign and destiny
            self.veh_states[veh_ID].origin, self.veh_states[veh_ID].destiny = (self.veh_states[veh_ID].destiny, self.veh_states[veh_ID].origin)
            new_route: tuple[str] = traci.simulation.findRoute(veh_edge, self.veh_states[veh_ID].destiny).edges
            traci.vehicle.setRoute(veh_ID, new_route)


    def check_cs_stop(self, veh_ID: str):
        """ Checks if the vehicle is waiting for too much time for it's stop CS and cancel the stop if it does. """

        next_stop_tuple: Any = traci.vehicle.getStops(veh_ID, 1)
        if next_stop_tuple and traci.vehicle.getWaitingTime(veh_ID) >= MAX_VEHICLE_WAITING_TIME:
            next_stop = next_stop_tuple[0]

            if next_stop.stoppingPlaceID:
                cs_lane: str = traci.chargingstation.getLaneID(next_stop.stoppingPlaceID)

                if cs_lane:
                    self.log(f"Vehicle {veh_ID} waited {MAX_VEHICLE_WAITING_TIME} seconds at it's stop. Canceling.", level=Vol.ESSENTIALS)
                    traci.vehicle.replaceStop(veh_ID, 0, "")    # Removing vehicle's stop.


    def update_lane_visits(self, veh_ID:str) -> None:
        """ Get's the given vehicle's current lane and updates the lane visits counter for that lane """

        lane_ID: str = traci.vehicle.getLaneID(veh_ID)
        if lane_ID and lane_ID[0] != ":":
            if lane_ID not in self.lane_data:
                self.lane_data[lane_ID] = LaneData(lane_ID, traci.lane.getLength(lane_ID), 0)
            self.lane_data[lane_ID].visits_count += 1


    # ===< Logging Methods >====

    def log_charge_level(self, veh_ID:str, interval: int = 1, needed: bool = False) -> None:
        """ Periodically log's the given vehicle battery level with timestamp """
        if needed or (LOG_CHARGE_LEVEL and (traci.simulation.getTime() % interval == 0)):
            self.log(f"Vehicle {veh_ID} charge_level = {traci.vehicle.getParameter(veh_ID, util.PAR_CHARGE_LEVEL)} Wh")


    def log_lane_visits(self) -> None:
        """ Writes the visists count for each lane in a separeted csv file. """
        try:
            with open(f"{self.base_filename}_lv.csv", "w") as lane_visits_log:
                for lane in self.lane_data:
                    lane_visits_log.write(f"{lane}, {self.lane_data[lane].lane_length}, {self.lane_data[lane].visits_count}\n")

        except IOError as error:
            print(error)

    def log_lowBatteryWaitTime(self) -> None:
        """ """
        try:
            with open(f"{self.base_filename}_lbt.csv", "w") as low_battery_log:
                for veh in self.veh_states:
                    low_battery_log.write(f"{veh}, {self.veh_states[veh]}")
        except IOError as error:
            print(error)


if __name__ == "__main__":
    params: TraciParameters = TraciParameters(
        sumocfg_file = "ev_test/ev_test.sumocfg",
        delay = 30,
        gui = True,
        verbose = True,
        end_time = 20_000
    )

    simulation = EV_Simulation(params)
    simulation.start()