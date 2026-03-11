# src/predefinitions.py
# -----------------------------------------------------------

# Helper specialized classes that defines some of the predefined scenarios used for the simulations and tests

# ===========================================================

from enum import IntEnum

from .params import (
    # === Default parameters:
    DEFAULT_INITIAL_LOG_FILENAME,
    DEFAULT_VALIDATION_LOG_FILENAME,
)

from .utils.sumo_setup import TraciParameters
from .runner import SimulationParameters, Runner


class Predefinitions(IntEnum):
    NONE    = 0,
    GRID    = 1,
    BD      = 2,
    BH      = 3,
    COLOGNE = 4


class TestGrid(Runner):
    def __init__(self, params: TraciParameters, sim_params: SimulationParameters):
        self.sim_initial_log_filename    = DEFAULT_INITIAL_LOG_FILENAME
        self.sim_validation_log_filename = DEFAULT_VALIDATION_LOG_FILENAME

        params.sumocfg_file       = "scenarios/ev_test_grid/ev_test.sumocfg"
        params.add_files          = "scenarios/ev_test_grid/ev_test.add.xml"

        #params.delay      = 30
        params.gui        = True
        params.verbose    = True

        sim_params.add_file = params.add_files
        super().__init__(params, sim_params)

    def initial_run(self):
        return super().initial_run()
    
    def validation_run(self):
        return super().validation_run()


class TestBD(Runner):
    def __init__(self, params: TraciParameters, sim_params: SimulationParameters):
        self.sim_initial_log_filename: str = DEFAULT_INITIAL_LOG_FILENAME
        self.sim_validation_log_filename: str = DEFAULT_VALIDATION_LOG_FILENAME

        params.sumocfg_file       = "scenarios/BD/test_bd.sumocfg"
        params.add_files          = "scenarios/BD/cs_test.add.xml"

        sim_params.add_file = params.add_files
        super().__init__(params, sim_params)

    def initial_run(self) -> None:
        return super().initial_run()
    
    def validation_run(self) -> None:
        return super().validation_run()


class TestCOLOGNE(Runner):
    def __init__(self, params: TraciParameters, sim_params: SimulationParameters):
        self.sim_initial_log_filename: str = DEFAULT_INITIAL_LOG_FILENAME
        self.sim_validation_log_filename: str = DEFAULT_VALIDATION_LOG_FILENAME

        params.sumocfg_file       = "scenarios/TAPASCologne-0.32.0/sim_cologne.sumocfg"
        params.add_files          = "scenarios/TAPASCologne-0.32.0/sim_cologne_cs.add.xml"

        sim_params.add_file = params.add_files
        super().__init__(params, sim_params)

    def initial_run(self) -> None:
        return super().initial_run()
    
    def validation_run(self) -> None:
        return super().validation_run()


class TestBH(Runner):
    def __init__(self, params: TraciParameters, sim_params: SimulationParameters):
        #self.sim_initial_log_filename: str = DEFAULT_INITIAL_LOG_FILENAME
        #self.sim_validation_log_filename: str = DEFAULT_VALIDATION_LOG_FILENAME

        params.sumocfg_file       = "scenarios/BH/bh.sumocfg"
        #params.add_files         = "scenarios/BH/bh.add.xml"

        params.add_files = sim_params.add_file
        super().__init__(params, sim_params)

    def initial_run(self) -> None:
        return super().initial_run()
    
    def validation_run(self) -> None:
        return super().validation_run()


def build_predefition(predef: Predefinitions, params: TraciParameters, sim_params: SimulationParameters) -> Runner:
    runner: Runner
    match predef:
        case Predefinitions.NONE:
            runner: Runner = Runner(params, sim_params)

        case Predefinitions.GRID:
            runner: Runner = TestGrid(params, sim_params)

        case Predefinitions.BD:
            runner: Runner = TestBD(params, sim_params)

        case Predefinitions.BH:
            runner: Runner = TestBH(params, sim_params)

        case Predefinitions.COLOGNE:
            runner: Runner = TestCOLOGNE(params, sim_params)

        case _:
            raise Exception("Invalid Predefinition.")
        
    return runner