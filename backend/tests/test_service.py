import asyncio

import pytest

from app.services.live import ConnectionManager, SimulatorService


class BlockingEngine:
    def tick(self):
        return []


class Queries:
    def status(self):
        raise AssertionError("Loop should not reach snapshot during this test")


@pytest.mark.asyncio
async def test_service_prevents_duplicate_loop_startup():
    service = SimulatorService(BlockingEngine(), Queries(), ConnectionManager(), tick_delay=60)

    assert await service.start() is True
    assert await service.start() is False
    assert service.is_running is True
    await asyncio.sleep(0)
    await service.stop()
    assert service.is_running is False

