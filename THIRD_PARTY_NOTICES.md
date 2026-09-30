# Third-party provenance

The application integrates third-party scientific software and data. It does not claim authorship of the connectome or upstream neural simulator.

## Scientific data

MaleCNS v1.0 by FlyEM / HHMI Janelia, University of Cambridge, MRC Laboratory of Molecular Biology, and Google Research.

- Source and attribution: https://male-cns.janelia.org/download/
- Licence: Creative Commons Attribution 4.0 International, https://creativecommons.org/licenses/by/4.0/
- Changes: the project exports a brain-space subset of soma/soma-tract positions, selected sensory populations, and seven neuron centerline skeletons into compact binary assets. Coordinates are recentered/scaled for the web scene. Branch pulses are illustrative animations rather than recorded biological activity. See frontend/public/data/malecns/manifest.json, backend/scripts/export_neural_scene.py, and docs/FLY_BRAIN_MAPPING.md.

## Neural simulator

The backend depends on flybrain 0.1.0 from the fly.ai project by alextitonis, distributed under the MIT licence. Upstream source and copyright notice: https://github.com/alextitonis/fly.ai/blob/main/LICENSE. Its upstream model credits are retained by the dependency and upstream documentation. The application supplies its own hiring state machine, inputs/outputs, persistence, API and visualizations.

Other Python and JavaScript dependencies are obtained through the retained manifests and lockfiles; package caches and installed dependency trees are excluded from this source repository. Their individual licences remain applicable.
