import ev_simulation as evs

if __name__ == "__main__":
    simulation = evs.EV_Simulation(
        config_file="ev_test/ev_test.sumocfg",
        delay=30,
        gui=True,
        verbose=True,
        end_time=20_000
    )

    simulation.start()