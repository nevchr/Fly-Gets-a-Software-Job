# Connectome performance

Measured locally on 2026-09-24 with Python 3.12, `flybrain 0.1.0`, MaleCNS v1.0, CPU mode, one fly, and the default 250 ms requested decision window. `FlyBrain.dt` is 20 ms, so each decision runs 13 steps or 260 simulated milliseconds.

## Results

| Measurement | Result |
|---|---:|
| Raw data load / `FlyBrain` construction | 0.64 s |
| First raw 13-step run before compilation warm-up | 1.87 s |
| Adapter initialization including one warm-up step | 2.42–2.53 s |
| Six consecutive adapter decisions | 87.6, 122.0, 144.1, 258.9, 134.9, 131.8 ms |
| Six-decision mean | 146.5 ms |
| Full persisted application-cycle mean across seven decisions | 120.5 ms |
| Six-decision wall time | 0.96 s |
| Six-decision process CPU time | 7.47 s |
| Approximate parallel CPU use | 7.76 logical-core equivalents |

The CPU figure is process CPU time divided by wall time, not a sampled whole-system utilization percentage. Processor-model inspection was unavailable in the execution sandbox.

## Acceptance cycle

A clean SQLite simulation using the real adapter completed in eight simulator ticks:

```text
JOB_FOUND -> JOB_VIEWED -> APPLICATION_SENT -> RESUME_SCANNED
-> RECRUITER_SCREEN_BOOKED -> RECRUITER_SCREEN_PASSED
-> TECHNICAL_ANSWERED -> BEHAVIORAL_ANSWERED -> CULTURE_REJECTION
```

That run made seven connectome decisions, reached technical and behavioral interviews, and returned to `SEARCHING_FOR_JOB`. The last decision observed 46,444 active neurons, a whole-network mean rate of 3.97 Hz, and a 130.5 ms wall latency. Both `DNa02` binary readouts were silent in that final window, so the documented lowest-index tie rule produced false/reject.

An isolated high-desirability application stimulus produced:

- left `LC10a` approach magnitude `0.5165` across 135 neurons;
- right `LC10a` avoidance magnitude `0.1077` across 140 neurons;
- 6,459 active neurons and 0.179 Hz whole-network mean rate;
- right `DNa02`: 0 spikes; left `DNa02`: 1 spike (`3.85 Hz` over 260 ms);
- resulting simulator decision: `true` / apply.

## Operational notes

- The connectome is loaded once. It is not reconstructed between decisions.
- Neural work happens inside the simulator tick already dispatched with `asyncio.to_thread()`, so it does not block FastAPI's event loop.
- CPU is the required baseline and works on this machine. `FLY_BRAIN_DEVICE=auto` will use CUDA only if the optional CuPy GPU stack is installed and `flybrain` reports an available device.
- WebSocket payloads contain only aggregates, named input/output groups, and at most 32 sampled neuron indices—not all 166,700 neurons.

