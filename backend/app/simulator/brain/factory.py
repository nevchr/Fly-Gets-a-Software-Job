from app.simulator.brain.mock import MockBrainAdapter


def create_brain_adapter(settings):
    backend = settings.brain_backend.strip().lower()
    if backend == "mock":
        return MockBrainAdapter(settings.simulation_seed)
    if backend == "connectome":
        from app.simulator.brain.fly_connectome import FlyConnectomeAdapter

        return FlyConnectomeAdapter(
            seed=settings.simulation_seed,
            device=settings.fly_brain_device,
            decision_ms=settings.fly_brain_decision_ms,
            data_dir=settings.fly_brain_data_dir or None,
        )
    raise ValueError("BRAIN_BACKEND must be connectome or mock")
