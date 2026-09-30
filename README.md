# Fly Gets a Software Job

One persistent fruit fly is trying to get hired in software. Every visitor watches the same career unfold: the same applications, interviews, rejections, rare offers, and questionable neural decisions.

The production backend now runs the open-source `flybrain 0.1.0` simulation of the [MaleCNS v1.0 adult male fruit-fly central nervous system](https://research.google/blog/a-connectomics-milestone-mapping-the-complete-male-fruit-fly-brain/). The published source connectome contains more than 166,000 neurons and 125 million synaptic contacts; the local `flybrain` runtime loads 166,700 neurons and 25,582,938 processed neuron-to-neuron model edges. A seeded mock backend remains available for tests and debugging, and the UI always identifies which backend is active.

## What is included

- FastAPI application with a continuously running, restart-safe state machine
- SQLite persistence for the active state, lifetime statistics, jobs, events, and interview attempts
- `BrainAdapter` interface, real `FlyConnectomeAdapter`, and deterministic `MockBrainAdapter`
- Explicit state-to-sensory encoding and descending-neuron action decoding
- Procedural satirical job postings and 55 technical interview questions across 11 categories, with varied stage and event writing
- REST status endpoints and a live WebSocket event stream
- React + TypeScript frontend styled as a live bug-cam broadcast, with a clearly labelled automated chat-style event log
- Original handmade 3D fly with a Blender rig, five animation clips, and live neural activity reactions
- Glass-walled 3D office with a San Francisco-inspired bay view, changing sunlight and skyline lights
- Interactive 3D MaleCNS anatomy: 125,020 mapped soma/soma-tract positions and seven traced neurons, with brightness driven by the simulator's spikes for those exact cells
- Live job/stage view, statistics, interview results, brain activity, and event feed
- Backend tests covering decisions, transitions, outcomes, statistics, persistence, interview tracking, and duplicate-loop protection

## Requirements

- Python 3.12 or newer
- Node.js 20 or newer
- npm or pnpm

No account, API key, paid service, Docker, or internet connection is needed after dependencies are installed.

## 1. Set up the backend

Open PowerShell in the repository root:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
flybrain download
Copy-Item .env.example .env
```

If `py` is unavailable but `python` is Python 3.12+, use `python -m venv .venv`.

## 2. Run the backend

With the backend virtual environment active:

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

The download is approximately 260 MB and is checksum-verified by `flybrain`. By default it is stored in `~/fly-data`. The simulator starts with FastAPI, initializes the real connectome once, resumes the saved career, and advances every 4.5 seconds by default. REST documentation is at <http://localhost:8000/docs>.

If data is missing, connectome mode exits with a direct `flybrain download` instruction. It never silently falls back to the mock brain.

## 3. Set up and run the frontend

Open a second PowerShell window in the repository root:

```powershell
cd frontend
pnpm install
Copy-Item .env.example .env
pnpm dev
```

`npm install` and `npm run dev` work as alternatives. Open <http://localhost:5173>.

## The handmade fly

The original Blender file remains at `C:\Users\chris\OneDrive\Documents\fly-v1.blend`. A snapshot of its state before rigging is `fly-v1-working.blend` in this project. Open `fly-v1-rigged.blend` to see the finished version. Its armature has 26 named bones, including three joints for each leg. The head, abdomen, wings, eyes, antennae, and all six legs move with the rig.

The Blender file contains `Idle`, `WingFlap`, `Walk`, `Type`, and `Startle` actions. Idle is the active NLA track when the file opens. To preview another clip, select `Fly_Armature`, open the NLA editor in the Animation workspace, mute Idle, and unmute the clip you want. Press Space to play; restore Idle when finished. Use Pose Mode to adjust individual bones.

`frontend/public/models/fly-v1.glb` is the web export. The page uses career stages to choose walking, typing, idle, or startled motion. Live neural activation changes movement speed, wing flutter, and eye glow. If WebGL or the model fails to load, the original SVG fly remains visible. The 3D viewer respects reduced-motion settings.

The main stage switches automatically between an application desk (job search through application result) and a video interview room (recruiter, technical, and behavioral rounds). A short broadcast camera-switch card announces the move and covers the 3D room change. The fly stays mounted across the switch. The technical interview panel shows the latest completed question, labelled as a recent question; the backend does not expose an unanswered live prompt. The Bug Chat sidebar is read-only and displays simulator events, not messages from real viewers.

## The neural map

The brain panel renders real MaleCNS v1.0 positions and seven real neuron centerline skeletons from the [HHMI Janelia MaleCNS download](https://male-cns.janelia.org/download/). Drag to rotate and scroll to zoom. The 125,020 overview points are the subset of `flybrain`'s annotated soma or soma-tract positions in brain space; they are not a full volumetric reconstruction of every neuron. The five colored sensory populations contain 489 mapped points corresponding to the exact groups stimulated by the backend. Those groups pulse independently according to their simulated firing rates. The colored branches are original SWC skeleton coordinates for seven labeled body IDs. When a traced cell spikes in a new decision, a bright surge follows its actual branch paths, and a brighter spark travels along one continuous branch selected from the largest brain-space fragment. This travel direction and speed are an **illustrative animation**, not a recording or prediction of where a biological spike propagated. Reduced-motion mode uses steady highlights instead. The panel does not show measured electrical activity or activity of every cell in a whole brain region.

The compact prebuilt web assets are in `frontend/public/data/malecns/`, so site visitors do not download the full scientific dataset. The export code is `backend/scripts/export_neural_scene.py`. To regenerate the assets, install backend dependencies and place the seven public `ID.swc` files listed in the manifest under `backend/data/malecns_swc/`, then run the script using the backend virtual environment. The raw SWCs are intentionally not stored in this project. The anatomy source is MaleCNS v1.0, credited to FlyEM / HHMI Janelia, University of Cambridge, MRC Laboratory of Molecular Biology, and Google Research, under CC BY 4.0.

The repeatable Blender scripts are in `blender/`. `finish_fly.py` rebuilds the rigged file and web export from the working snapshot; it will replace those generated files, so keep manual edits in a separate `.blend` copy.

## Tests and production build

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -q

# Optional: load and exercise the real 260 MB connectome
$env:RUN_FLYBRAIN_INTEGRATION='1'
pytest -q -m integration
Remove-Item Env:RUN_FLYBRAIN_INTEGRATION

cd ..\frontend
pnpm build
```

The frontend output is written to `frontend/dist`.

## Persistent data

The SQLite database lives at `backend/data/fly_career.db`. It is created automatically and is never recreated during ordinary startup.

To intentionally reset the career, stop the backend and delete only that file:

```powershell
Remove-Item -LiteralPath .\backend\data\fly_career.db
```

The next backend start creates a fresh fly. SQLite sidecar files may briefly appear while the server is running; never delete the database while the backend is active.

## Simulation speed

Edit `backend/.env`:

```dotenv
SIMULATION_TICK_SECONDS=4.5
SIMULATION_SPEED=1.0
```

For a faster development run, set `SIMULATION_SPEED=8`. The effective delay is `SIMULATION_TICK_SECONDS / SIMULATION_SPEED`, with a small safety floor. Restart the backend after changing either setting.

The simulated San Francisco clock has 96 ticks per day (15 simulated minutes per tick, about 7.2 real minutes at the default speed). From 7:00 AM to 7:00 PM, applications can receive hiring decisions and the fly can interview. After hours it continues to find jobs and submit applications; replies queue for the next morning, and any interview already in progress pauses. The window view and room lighting follow this same clock. This is an accelerated fictional schedule, not real Pacific time.

## Brain configuration

`backend/.env` supports:

```dotenv
BRAIN_BACKEND=connectome
FLY_BRAIN_DEVICE=auto
FLY_BRAIN_DECISION_MS=250
FLY_BRAIN_DATA_DIR=
```

Supported backends are `connectome` and `mock`. Connectome is the default. `auto` chooses CUDA only when the optional GPU dependencies and a compatible NVIDIA GPU are available; otherwise it uses CPU. Leave the data directory blank to use `~/fly-data`.

For fast tests or debugging:

```powershell
$env:BRAIN_BACKEND='mock'
uvicorn app.main:app --reload --port 8000
```

## Architecture

The backend advances exactly one persisted state-machine step per tick. A tick is performed in a worker thread, so SQLite work does not block FastAPI's event loop. The application lifespan starts one guarded simulator task and cancels it cleanly on shutdown. Each tick commits before its new events and updated snapshot are sent to all WebSocket clients.

All applicant choices and hiring outcomes go through `BrainAdapter`. Job generation and question selection are environment inputs rather than fly decisions. `encoding.py` normalizes simulator state and stimulates documented `LC10a`, `LC4`, `LPLC2`, and `LPLC1` visual projection populations. The unchanged MaleCNS network advances for 13 neural steps, and `decoding.py` converts identified descending-neuron spike rates into action indices without a Python RNG fallback.

One `FlyBrain` object lives for the backend process. Its membrane potentials, previous spikes, step count, and noise state continue across career decisions. Neural work occurs in the simulator's worker thread, so FastAPI's event loop remains responsive. See [the complete mapping](docs/FLY_BRAIN_MAPPING.md) and [measured performance](docs/PERFORMANCE.md).

### Dataset provenance

This is the same complete male CNS release described by [Google Research](https://research.google/blog/a-connectomics-milestone-mapping-the-complete-male-fruit-fly-brain/) and published by the [HHMI Janelia FlyEM team](https://www.janelia.org/project-team/flyem/male-cns-connectome), in collaboration with the University of Cambridge and MRC Laboratory of Molecular Biology. It covers the central brain, optic lobes, and ventral nerve cord and is available under CC BY.

The two connection totals in this project are intentionally not interchangeable:

- **125 million source synaptic contacts** is the biological dataset-scale figure reported for the complete map.
- **25,582,938 model edges** is the number of confidence-filtered, neuron-to-neuron weight entries loaded by `flybrain` after synapses between a pair of neurons have been aggregated and converted into the simulation network.

## Scientific honesty

- Connectivity comes from the real, expert-proofread MaleCNS v1.0 connectome dataset produced by HHMI Janelia, Cambridge/MRC LMB, and Google Research.
- Neurons use `flybrain`'s simplified computational leaky integrate-and-fire dynamics.
- Job-feature sensory encoding and action decoding are designed by this project.
- The fly does not understand jobs, programming languages, interview questions, or English.
- This is not an LLM, a trained job policy, biologically exact simulation, or digitized consciousness.

## Current limitations

- The simulator runs in one backend process. Multiple server workers would each start a loop; run V1 with the default single worker.
- Offers end as a logged career event and the eternal job search resumes on the next application cycle.
- Schema migrations are not yet included; V1 initializes new tables directly with SQLAlchemy.
- Jobs and interview questions are local fixtures, not real listings.
- `flybrain 0.1.0` has no supported dynamic-state checkpoint API. SQLite career state survives restarts, but transient membrane and spike state starts fresh from the configured seed.
- The hand-designed interface uses sparse descending populations. Silent-output ties deterministically choose the lowest action index, which can bias behavior.

## Next milestone

Calibrate the job-task interface empirically without modifying the connectome: collect labelled stimulus/output episodes, measure action stability across seeds, compare the present hand-written decoder with an explicitly disclosed frozen linear readout, and add a supported neural-state checkpoint only if upstream `flybrain` gains a stable serialization contract.
