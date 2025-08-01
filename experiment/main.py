import ev_simulation as evs

def initial_run() -> None:
    simulation: evs.Simulation = evs.EV_Simulation(
        config_file="ev_test_grid/ev_test.sumocfg",
        gui_settings_files="ev_test_grid/ev_test.view.xml",
        delay=30,
        gui=True,
        verbose=True,
        end_time=5500
    )

    print("\nStarting Initial Run:\n")
    simulation.start()

def validation_run() -> None:
    simulation: evs.Simulation = evs.EV_Simulation(
        config_file="ev_test_grid/ev_test.sumocfg",
        gui_settings_files="ev_test_grid/ev_test.view.xml",
        add_files="ev_test_grid/cs_test.add.xml",
        sim_log_filename="data/validation.log",
        delay=30,
        gui=True,
        verbose=True,
        end_time=5500
    )

    print("\nStarting Validation Run:\n")
    simulation.start()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Runs the core of the Electric vehicle Simulation")
    parser.add_argument("-opt", "--option", type=str, default="both", help="Simulation's running option.\n"\
                        "- \"first\": Runs only the intial run of the simulation.\n"\
                        "- \"second\": Runs only the validation run of the simulation\n"\
                        "- \"both\": Runs both the first and validation runs of the simulation.")

    args = parser.parse_args()

    match args.option:
        case "first":
            initial_run()
        
        case "second":
            validation_run()

        case "both":
            initial_run()
            validation_run()

        case _:
            print("Invalid running option.")