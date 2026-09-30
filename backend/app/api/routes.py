from fastapi import APIRouter, Query, Request, WebSocket, WebSocketDisconnect

from app.schemas import InterviewStatsResponse, JobResponse, StatsResponse, StatusResponse


router = APIRouter()


@router.get("/api/status", response_model=StatusResponse)
def get_status(request: Request):
    return request.app.state.queries.status()


@router.get("/api/stats", response_model=StatsResponse)
def get_stats(request: Request):
    return request.app.state.queries.stats()


@router.get("/api/events")
def get_events(request: Request, limit: int = Query(default=100, ge=1, le=500)):
    return request.app.state.queries.events(limit)


@router.get("/api/current-job", response_model=JobResponse | None)
def get_current_job(request: Request):
    return request.app.state.queries.current_job()


@router.get("/api/interview-stats", response_model=InterviewStatsResponse)
def get_interview_stats(request: Request):
    return request.app.state.queries.interview_stats()


@router.websocket("/ws/live")
async def live_stream(websocket: WebSocket):
    app = websocket.scope["app"]
    manager = app.state.connection_manager
    await manager.connect(websocket)
    try:
        await websocket.send_json(app.state.simulator_service.snapshot())
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

