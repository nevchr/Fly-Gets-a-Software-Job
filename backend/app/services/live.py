import asyncio
from contextlib import suppress

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def broadcast(self, payload: dict) -> None:
        dead = []
        for connection in tuple(self._connections):
            try:
                await connection.send_json(payload)
            except Exception:
                dead.append(connection)
        for connection in dead:
            self.disconnect(connection)


class SimulatorService:
    def __init__(self, engine, queries, manager: ConnectionManager, tick_delay: float):
        self.engine = engine
        self.queries = queries
        self.manager = manager
        self.tick_delay = tick_delay
        self._task: asyncio.Task | None = None
        self._start_lock = asyncio.Lock()

    @property
    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def start(self) -> bool:
        async with self._start_lock:
            if self.is_running:
                return False
            self._task = asyncio.create_task(self._run(), name="fly-career-simulator")
            return True

    async def stop(self) -> None:
        if not self._task:
            return
        self._task.cancel()
        with suppress(asyncio.CancelledError):
            await self._task
        self._task = None

    async def _run(self) -> None:
        while True:
            events = await asyncio.to_thread(self.engine.tick)
            payload = await asyncio.to_thread(self.snapshot, events)
            await self.manager.broadcast(payload)
            await asyncio.sleep(self.tick_delay)

    def snapshot(self, raw_events: list[dict] | None = None) -> dict:
        events = raw_events or []
        current_job = self.queries.current_job()
        return {
            "kind": "simulation_update",
            "events": events,
            "status": self.queries.status().model_dump(mode="json"),
            "stats": self.queries.stats().model_dump(mode="json"),
            "current_job": current_job.model_dump(mode="json") if current_job else None,
        }
