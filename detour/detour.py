sumoBinary = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui.exe"
#sumoBinary = "sumo-gui.exe"
sumo_config = [
    sumoBinary,
    "--net-file", "./config/network.net.xml",
    "--route-files", "./config/trips.trips.xml",
    "--gui-settings-file", "./config/viewSettings.xml",
    "--delay", "200",
    "--start"
]

import traci
import traci.constants as tc

VEHICLES = ["1", "4", "8"]

def avoid_edge(vehID:str, edgeID):
    traci.vehicle.setAdaptedTraveltime(vehID, edgeID, float("inf"))
    traci.vehicle.rerouteTraveltime(vehID)  # To force the car to recalculate it's route.

if __name__ == "__main__":
    traci.start(sumo_config)

    # The loop must run while there is vehicles or persons on the network. 
    while(traci.simulation.getMinExpectedNumber() > 0):
        vehs = traci.edge.getLastStepVehicleIDs("origin")
        for vehID in vehs:
            if(vehID in VEHICLES):
                avoid_edge(vehID, "closed")
                traci.vehicle.setColor(vehID, [255,0,0])

        traci.simulationStep()

    traci.close()