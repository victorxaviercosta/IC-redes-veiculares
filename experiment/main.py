import ev_simulation as evs

if __name__ == "__main__":
    simulation = evs.EV_Simulation(
        config_file="ev_test_grid/ev_test.sumocfg",
        gui_settings_files="ev_test_grid/ev_test.view.xml",
        delay=30,
        gui=True,
        verbose=True,
        end_time=20_000
    )

    simulation.start()