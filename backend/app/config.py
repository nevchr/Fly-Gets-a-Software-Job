from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    database_url: str = f"sqlite:///{(BACKEND_DIR / 'data' / 'fly_career.db').as_posix()}"
    simulation_tick_seconds: float = 4.5
    simulation_speed: float = 1.0
    simulation_seed: int = 314159
    max_stored_events: int = 1000
    simulator_autostart: bool = True
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    brain_backend: str = "connectome"
    fly_brain_device: str = "auto"
    fly_brain_decision_ms: int = 250
    fly_brain_data_dir: str = ""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def tick_delay(self) -> float:
        return max(0.02, self.simulation_tick_seconds / max(self.simulation_speed, 0.01))

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
