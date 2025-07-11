import simulation as sim
from simulation import Simulation
import traci
import traci.exceptions
from typing import override


EV_MAX_BATTERY_CAPACITY: float = 30000
INTIAL_BATTERY_PERCENTAGE: float = 0.4
LOW_BATTERY_PERCENTAGE: float = 0.25

LOG_STATION_DISTANCES: bool = False
LOG_END_OF_ROUTE_REROUTE: bool = False

PAR_CHARGE_LEVEL:str = "device.battery.chargeLevel"

class EV_Simulation(sim.Simulation):
    def __init__(self, 
                 config_file:str, add_files:str = "", 
                 tripifo_out_file:str = "", log_file:str = "", 
                 delay:int = 0, 
                 gui:bool = False, 
                 gui_settings_files:str = "", 
                 auto_start:bool = False, 
                 verbose:bool = False,
                 end_time:int = 3600):
        super().__init__(config_file, add_files, tripifo_out_file, log_file, delay, gui, gui_settings_files, auto_start, verbose, end_time)
        self.veh_states: dict = {}
        self.reroutes:list[tuple[str, str, str]] = [] # [(veh_ID, original_destiny, new_destiny)]

    @override
    def pre_start(self) -> None:
        for veh_ID in traci.vehicle.getIDList(): # For each vehicle currently in the network
            if traci.vehicle.getTypeID(veh_ID) == "ElectricCar":
                self.set_charge_level(veh_ID, EV_MAX_BATTERY_CAPACITY * INTIAL_BATTERY_PERCENTAGE)
                Simulation.log(f"Starting Battery_Level: {EV_MAX_BATTERY_CAPACITY * INTIAL_BATTERY_PERCENTAGE}")

    @override
    def step(self) -> None:
        for veh_ID in traci.vehicle.getIDList(): # For each vehicle currently in the network
            if traci.vehicle.getTypeID(veh_ID):
                veh_route: tuple[str] = traci.vehicle.getRoute(veh_ID)

                # At the first Check initializates the origin and destination of the vehicle.
                if veh_ID not in self.veh_states:
                    self.veh_states[veh_ID] = {}
                    self.veh_states[veh_ID]["origin"] = veh_route[0]
                    self.veh_states[veh_ID]["destiny"] = veh_route[-1]

                    from random import random
                    self.set_charge_level(veh_ID, EV_MAX_BATTERY_CAPACITY * max(0.3, random()))

                
                # Checking if vehicle have been previously rerouted:
                handle_low_battery:bool = True
                for rr in self.reroutes:
                    if (rr[0] == veh_ID):
                        handle_low_battery = False # No need to handle battery level since it was already resolved.

                        # If the vehicle is stopped at it's current destiny.
                        if(traci.vehicle.getSpeed(veh_ID) == 0 and rr[-1] == traci.vehicle.getRoadID(veh_ID)):
                            traci.vehicle.changeTarget(veh_ID, rr[1])
                            self.reroutes.remove(rr)
                            Simulation.log(f"Vehicle {veh_ID} route reestablished: \n\tFrom: {rr[-1]} \n\tTo: {rr[1]}")
                            #print(f"{traci.vehicle.getRoute(veh_ID)}")

                if handle_low_battery:
                    self.check_destiny_reached(veh_ID)

                self.log_charge_level(veh_ID)

                self.check_charge_level(veh_ID, handle_low_battery)



    def set_charge_level(self, veh_ID:str, value:int) -> None:
        traci.vehicle.setParameter(veh_ID, PAR_CHARGE_LEVEL, str(value))



    def get_charge_level(self, veh_ID:str) -> float:
        return float(traci.vehicle.getParameter(veh_ID, PAR_CHARGE_LEVEL))



    def check_charge_level(self, veh_ID:str, handle_low_battery:bool) -> None:
        battery_charge:float = self.get_charge_level(veh_ID)
        veh_position: tuple[float, float] = traci.vehicle.getPosition(veh_ID)

        level: float = max(0, min(1, (battery_charge / EV_MAX_BATTERY_CAPACITY)))
        if level < 0.5:
            color:tuple[int] = (255, int(255 * 2 * level), 0)
        else:
            color:tuple[int] = (int(255 * 2 * (1 - level)), 255, 0)

        traci.vehicle.setColor(veh_ID, color)

        # If vehicle have low battery:
        if handle_low_battery and (battery_charge <= (EV_MAX_BATTERY_CAPACITY * LOW_BATTERY_PERCENTAGE)):
            Simulation.log(f"{veh_ID} Low Battery: {battery_charge}Wh")
            
            closest_station = self.search_nearest_station(veh_position)

            # if there is any nearest station:
            if closest_station:
                self.reroute_vehicle(veh_ID, closest_station)



    def search_nearest_station(self, veh_pos:tuple[float]) -> str:
        """ Searches for the nearest station from the given vehicle position (For now it only considers euclidian distance). """
        #Simulation.log(f"Searching Nearest Station")

        closest_station:str = ""
        min_distance:float = float("inf")

        for charge_station_ID in traci.chargingstation.getIDList():
            station_position:tuple[float, float] = get_station_postion(charge_station_ID)

            # Calculating euclidian distance between the vehicle and the lane.
            distance:float = ((veh_pos[0] - station_position[0])**2 + (veh_pos[1] - station_position[1])**2)**0.5

            if LOG_STATION_DISTANCES:
                Simulation.log(f"\t{charge_station_ID} - distance: {distance} - position: {station_position}")

            if distance < min_distance:
                min_distance = distance
                closest_station = charge_station_ID

        Simulation.log(f"Found closest station: {closest_station}")
        return closest_station
    

    def reroute_vehicle(self, veh_ID:str, closest_station:str) -> None:
        original_route:tuple[str] = traci.vehicle.getRoute(veh_ID)
        original_destiny:str = original_route[-1] if original_route else None

        station_lane_ID:str = traci.chargingstation.getLaneID(closest_station)

        try:
            # Changing vehicle destiny to the closest_station's edge.
            new_destiny:str = station_lane_ID.split('_')[0]
            if(new_destiny == traci.vehicle.getLaneID(veh_ID).split('_')[0]):
                Simulation.log(f"Closest_station is already in {veh_ID}'s lane. Skiping.")
                return

            traci.vehicle.changeTarget(veh_ID, new_destiny)

            # Adding a charging stop at the closest_station for [duration] seconds.
            traci.vehicle.setChargingStationStop(veh_ID, closest_station, duration=500)
            traci.vehicle.setStopParameter(veh_ID, 0, "parking", "true") # This way, the vehicles park to use the charging station (beside the lane).
        
        except traci.exceptions.TraCIException as excp:
            Simulation.log(f"Error while seting Station stop for vehicle {veh_ID}: \n\t[Exception] {excp}")
            return

        # Add's the vehicle to the list of rerouted vehicles
        self.reroutes.append((veh_ID, original_destiny, new_destiny))

        Simulation.log(f"Vehicle {veh_ID} rerouted: \n\tOriginalDes: {original_destiny} \n\tNewDest: {new_destiny}")


    def check_destiny_reached(self, veh_ID:str):
        """ Checks if the vehicle reched it's destiny and reroutes it to it's previous origin. """

        veh_edge: str = traci.vehicle.getRoadID(veh_ID)
        
        if veh_edge == self.veh_states[veh_ID]["destiny"]:
            if LOG_END_OF_ROUTE_REROUTE:
                Simulation.log(f"Rerouting {veh_ID} from {self.veh_states[veh_ID]["destiny"]} to {self.veh_states[veh_ID]["origin"]} ({veh_edge})")

            # Swaps orign and destiny
            self.veh_states[veh_ID]["origin"], self.veh_states[veh_ID]["destiny"] = (self.veh_states[veh_ID]["destiny"], self.veh_states[veh_ID]["origin"])
            new_route: tuple[str] = traci.simulation.findRoute(veh_edge, self.veh_states[veh_ID]["destiny"]).edges
            traci.vehicle.setRoute(veh_ID, new_route)


    def log_charge_level(self, veh_ID:str) -> None:
        if(traci.simulation.getTime() % 500 == 0):
            Simulation.log(f"Vehicle {veh_ID} charge_level = {traci.vehicle.getParameter(veh_ID, PAR_CHARGE_LEVEL)}Wh")



def get_station_postion(station_ID:str) -> tuple[float,float]:
    station_lane_ID: str = traci.chargingstation.getLaneID(station_ID)
    station_pos:str = traci.chargingstation.getParameter(station_ID, "pos")

    if station_pos:
        station_position:tuple[float,float] = (float(station_pos[0]), float(station_pos[1]))

    # In this case there's only the realtive position of the station along the lane, so it's needed to calculate the absolute
    # postion of the station by getting the absolute positions in the lane's shape.
    else:
        lane_shape:list[tuple[float,float]] = traci.lane.getShape(station_lane_ID)
        station_start:float = traci.chargingstation.getStartPos(station_ID)
        
        # Searching at each segment of the lane and calculating the approximate absolute position for the vehicles.
        sub_length:float = 0
        for i in range(len(lane_shape) - 1):
            x0, y0 = lane_shape[i]
            x1, y1 = lane_shape[i+1]

            segment_len:float = ((x0 - x1)**2 + (y0 - y1)**2)**0.5 # Euclidian distance between the points.
            sub_length = sub_length + segment_len

            if station_start <= sub_length:
                # Using Similar Triangles to calculate the approximate position.
                station_position: tuple[float,float] = ( (x0 + (station_start/segment_len) * (x1-x0)),
                                                         (y0 + (station_start/segment_len) * (y1-y0)) )
                break

    return station_position


if __name__ == "__main__":
    simulation = EV_Simulation(
        config_file="ev_test/ev_test.sumocfg",
        delay=30,
        gui=True,
        verbose=True,
        end_time=20_000
    )

    simulation.start()