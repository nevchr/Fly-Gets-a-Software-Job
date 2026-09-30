from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_rest_api_and_websocket_snapshot(tmp_path):
    database_url = f"sqlite:///{(tmp_path / 'api.db').as_posix()}"
    app = create_app(Settings(database_url=database_url, simulator_autostart=False))
    app.state.simulation_engine.tick()

    with TestClient(app) as client:
        status = client.get("/api/status")
        stats = client.get("/api/stats")
        events = client.get("/api/events")
        current_job = client.get("/api/current-job")
        interview_stats = client.get("/api/interview-stats")

        assert status.status_code == 200
        assert status.json()["stage"] == "VIEWING_JOB"
        assert stats.json()["jobs_viewed"] == 1
        assert events.json()[0]["type"] == "JOB_FOUND"
        assert current_job.json()["company_name"]
        assert interview_stats.json()["total"] == 0

        with client.websocket_connect("/ws/live") as websocket:
            snapshot = websocket.receive_json()
            assert snapshot["kind"] == "simulation_update"
            assert snapshot["status"]["tick_count"] == 1
            assert snapshot["current_job"]["id"] == current_job.json()["id"]
