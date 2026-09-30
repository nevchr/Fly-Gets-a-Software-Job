from app.database import initialize_database, make_engine, make_session_factory
from app.models import CareerStats, SimulationState
from app.simulator.brain import MockBrainAdapter
from app.simulator.engine import SimulationEngine


def test_state_survives_engine_and_database_reopen(tmp_path):
    database_url = f"sqlite:///{(tmp_path / 'persistent.db').as_posix()}"
    first_db = make_engine(database_url)
    initialize_database(first_db)
    first_engine = SimulationEngine(make_session_factory(first_db), MockBrainAdapter(9), 9)
    first_engine.tick()
    first_db.dispose()

    second_db = make_engine(database_url)
    initialize_database(second_db)
    Session = make_session_factory(second_db)
    with Session() as session:
        assert session.get(CareerStats, 1).jobs_viewed == 1
        assert session.get(SimulationState, 1).tick_count == 1
        assert session.get(SimulationState, 1).active_application_id is not None
    second_db.dispose()

