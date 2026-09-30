# Fly brain input and output mapping

This project uses the real connectivity and fixed synaptic weights distributed by `flybrain` from the MaleCNS v1.0 dataset. The meanings assigned to job features and actions are an interface designed for this simulator; they are not meanings present in the fly.

## Dataset provenance

MaleCNS v1.0 is the complete adult male *Drosophila* central nervous system connectome produced by the HHMI Janelia FlyEM team with the University of Cambridge, MRC Laboratory of Molecular Biology, and Google Research. The source includes the central brain, optic lobes, and ventral nerve cord and was annotated and proofread by human experts.

- [Google Research announcement and project overview](https://research.google/blog/a-connectomics-milestone-mapping-the-complete-male-fruit-fly-brain/)
- [HHMI Janelia Male CNS dataset page](https://www.janelia.org/project-team/flyem/male-cns-connectome)
- [MaleCNS exploration and downloads](https://male-cns.janelia.org/)

Google Research reports more than 166,000 neurons and 125 million synaptic connections in the complete source map. The `flybrain 0.1.0` prebuilt arrays used here contain exactly 166,700 neurons and 25,582,938 nonzero neuron-to-neuron model edges. The latter is smaller because it counts processed pairwise weight entries after confidence filtering and aggregation, not individual biological synaptic contacts. The app labels these separately rather than presenting them as conflicting measurements.

## Pipeline

```text
BrainContext -> normalized features -> visual projection neurons
             -> stateful MaleCNS simulation -> descending-neuron spike rates
             -> deterministic action index
```

The correct technical-interview answer is never part of the input. The simulator evaluates the selected index only after the connectome has produced it.

## Numeric features

All values are clamped to `[0, 1]`.

| Feature | Mapping |
|---|---|
| `salary_normalized` | `(salary - 40,000) / 160,000` |
| `experience_gap` | required years divided by 10; V1 treats the fly as having zero industry years |
| `tech_stack_match` | procedural qualification match, already `[0, 1]` |
| `remote_score` | remote `1.0`, hybrid `0.55`, onsite `0.1` |
| `job_difficulty` | difficulty 1–5 mapped linearly |
| `application_length` | 1–40 form fields mapped linearly |
| `company_prestige` | first 32 bits of SHA-256 of the fictional company name, divided by `2^32-1`; stable but intentionally arbitrary |
| `absurdity_score` | matched absurd-requirement cues divided by 3 |
| `question_difficulty` | difficulty 1–3 mapped linearly |
| `category_embedding` | fixed position in the 11-category question list, divided by 10 |
| `number_of_choices` | 2–6 choices mapped linearly |
| `previous_answer_correct` | false `0`, true `1`; used only after an answer when the hiring outcome is decided |
| `recent_accuracy` | lifetime correct answers divided by lifetime questions; `0.5` before any answer |
| `interview_stage` | fixed state-machine position divided by 8 |
| `recent_rejection_streak` | streak divided by 12 |
| `company_desirability` | current procedural qualification match |
| `current_performance` | recent accuracy or the predefined behavioral-style score |

## Sensory populations

The same stimulus is applied on each 20 ms neural step in a decision window. The default requested window is 250 ms; the 20 ms integration step rounds that up to 13 steps, or 260 ms. Magnitudes are added directly to membrane voltage and capped at `0.65`, below the upstream encoder's usual `0.8` cap.

| Simulator channel | MaleCNS input | Magnitude | Why this population |
|---|---|---|---|
| Approach/desirability | left `LC10a` (135 neurons) | `0.10 + 0.50 × mean(salary, match, remote, prestige, performance)` | `LC10a` tracks a moving target during male courtship and has a documented ipsilateral path to `DNa02` steering |
| Avoidance/cost | right `LC10a` (140 neurons) | `0.10 + 0.50 × mean(experience gap, difficulty, form length, absurdity, rejection streak)` | Uses the symmetric side of the same documented chase-to-steering pathway; left/right as approach/avoid is our convention |
| Threat | right `LC4` (55 neurons) | `0.05 + 0.45 × max(difficulty, absurdity)` | `LC4` is a documented fast-looming/escape visual projection population |
| Looming workload | right `LPLC2` (91 neurons) | `0.05 + 0.40 × max(experience gap, form length)` | `LPLC2` responds to looming objects and is a documented input to the giant-fiber escape path |
| Choice uncertainty | left `LPLC1` (68 neurons) | `0.05 + 0.40 × mean(question difficulty, inverse accuracy, choice count)` | `LPLC1` detects small approaching objects; using it for abstract uncertainty is an imposed analogy |

These populations and counts are resolved from the loaded dataset by cell type and side. No neuron IDs are invented or randomly selected.

## Output populations

The decoder counts spikes during the decision window and compares per-neuron spike rates. Exact ties select the lowest action index. No Python random number generator chooses the result.

Binary decisions use the symmetric `DNa02` steering neurons:

| Index | Meaning | Output population |
|---|---|---|
| 0 | false / skip / reject | right `DNa02` (`steer_R`, 1 neuron) |
| 1 | true / apply / pass / accept | left `DNa02` (`steer_L`, 1 neuron) |

Multiple-choice decisions use up to six distinct documented descending/motor-oriented groups:

| Index | Output group | Biological association |
|---|---|---|
| 0 | left `DNa02` | steering |
| 1 | right `DNa02` | steering |
| 2 | bilateral `DNp01` | giant-fiber escape take-off |
| 3 | bilateral `DNg100` | forward walking |
| 4 | bilateral `MDN` | backward walking |
| 5 | bilateral `pIP10` | male courtship-song command |

The biological labels explain the populations, not the software-job option assigned to an index.

## State and scientific limitations

- One `FlyBrain` object is created at backend startup. Its membrane potentials, previous spikes, noise generator, step counter, and refractory state continue across decisions. The adapter never calls `reset()` during the career.
- `flybrain 0.1.0` exposes no supported dynamic-state serialization API. Career state remains in SQLite, but transient membrane state starts from a new seeded brain after a process restart. This limitation is not hidden or simulated away.
- The connectivity is real MaleCNS v1.0 connectome data. The leaky integrate-and-fire neuron dynamics are computational models with global hand-calibrated parameters, not biologically exact cells.
- Sensory encoding and action decoding are designed by this project. The fly does not understand companies, salaries, programming, or English.
- This is neither a trained policy nor an LLM, and it is not digitized consciousness.
- Identified output populations are very small and often do not spike in a short window. Deterministic tie-breaking can therefore bias low-numbered actions. A trained readout would change the scientific claim and is deliberately not used here.

The population choices follow the upstream `flybrain/eyes.py`, `inject.py`, quickstart notebook, and SSH Fighter decoder patterns.
