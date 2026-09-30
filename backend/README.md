# Backend

FastAPI owns the persistent simulator loop and API. The state machine never knows whether its `BrainAdapter` is mock or connectome-backed. Production defaults to the real MaleCNS v1.0 connectome; tests explicitly use the mock backend.

From this directory, after activating the virtual environment:

```powershell
pip install -r requirements-dev.txt
flybrain download
uvicorn app.main:app --reload --port 8000
```

Run ordinary tests with `pytest -q`. To run the optional 260 MB integration test, set `RUN_FLYBRAIN_INTEGRATION=1`. API documentation is available at <http://localhost:8000/docs>.
