from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import Settings
from app.database import initialize_database, make_engine, make_session_factory
from app.services.live import ConnectionManager, SimulatorService
from app.services.queries import SimulationQueries
from app.simulator.brain import create_brain_adapter
from app.simulator.engine import SimulationEngine


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    db_engine = make_engine(settings.database_url)
    initialize_database(db_engine)
    session_factory = make_session_factory(db_engine)
    brain = create_brain_adapter(settings)
    simulation_engine = SimulationEngine(
        session_factory,
        brain,
        settings.simulation_seed,
        settings.max_stored_events,
    )
    queries = SimulationQueries(session_factory, brain, settings.tick_delay)
    manager = ConnectionManager()
    service = SimulatorService(simulation_engine, queries, manager, settings.tick_delay)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if settings.simulator_autostart:
            await service.start()
        yield
        await service.stop()
        db_engine.dispose()

    app = FastAPI(
        title="Fly Gets a Software Job API",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    app.include_router(router)
    app.state.settings = settings
    app.state.db_engine = db_engine
    app.state.session_factory = session_factory
    app.state.brain = brain
    app.state.simulation_engine = simulation_engine
    app.state.queries = queries
    app.state.connection_manager = manager
    app.state.simulator_service = service
    return app


app = create_app()
