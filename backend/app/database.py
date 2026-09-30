from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def make_engine(database_url: str):
    if database_url.startswith("sqlite:///"):
        db_path = database_url.removeprefix("sqlite:///")
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
        database_url,
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
    )


def make_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def initialize_database(engine) -> None:
    from app.models import CareerStats, SimulationState

    Base.metadata.create_all(engine)
    Session = make_session_factory(engine)
    with Session.begin() as session:
        if session.get(SimulationState, 1) is None:
            session.add(SimulationState(id=1))
        if session.get(CareerStats, 1) is None:
            session.add(CareerStats(id=1))

