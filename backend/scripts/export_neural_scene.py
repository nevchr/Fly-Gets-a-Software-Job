"""Export a compact, anatomically grounded MaleCNS scene for the web viewer.

Run from the repository root with backend/.venv/Scripts/python.exe. The source
SWCs are the public MaleCNS v1.0 centerline skeletons documented by Janelia.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from flybrain.data import DATA


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "backend" / "data" / "malecns_swc"
OUTPUT = ROOT / "frontend" / "public" / "data" / "malecns"
SKELETON_SOURCE = (
    "https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/"
    "skeletons-malecns/skeletons-swc/"
)
BODY_IDS = (
    (10573, "LC10a_L", "approach input", "#66d6db"),
    (21065, "LC10a_R", "avoidance input", "#8fb8ee"),
    (16128, "LC4_R", "threat input", "#e9a078"),
    (14465, "LPLC2_R", "workload input", "#c8aaec"),
    (12052, "LPLC1_L", "uncertainty input", "#e5cf7e"),
    (523769, "DNa02_L", "approach output", "#cbf570"),
    (10360, "DNa02_R", "avoidance output", "#ed8068"),
)
INPUT_POPULATIONS = (
    ("approach", "LC10a", "L", "#66d6db"),
    ("avoidance", "LC10a", "R", "#8fb8ee"),
    ("threat", "LC4", "R", "#e9a078"),
    ("looming_work", "LPLC2", "R", "#c8aaec"),
    ("choice_uncertainty", "LPLC1", "L", "#e5cf7e"),
)
BRAIN_Z_LIMIT = 50_000  # separates the brain from the ventral nerve cord


def transform(points: np.ndarray, center: np.ndarray, scale: float) -> np.ndarray:
    result = (points - center) * scale
    result[:, 1] *= -1  # image Y increases ventrally; display dorsal side up
    return result.astype("<f4")


def parse_swc(path: Path, soma_position: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    nodes: dict[int, tuple[float, float, float]] = {}
    links: list[tuple[int, int]] = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.startswith("#") or not line.strip():
                continue
            fields = line.split()
            node_id = int(fields[0])
            nodes[node_id] = tuple(float(value) for value in fields[2:5])
            parent = int(fields[6])
            if parent != -1:
                links.append((node_id, parent))
    # The SWC is a branching tree. Use path length from the node nearest the
    # annotated soma so a visual wave follows branches instead of screen X/Y.
    neighbors: dict[int, list[int]] = {node_id: [] for node_id in nodes}
    for child, parent in links:
        if parent in nodes:
            neighbors[child].append(parent)
            neighbors[parent].append(child)
    distances: dict[int, float] = {}
    while len(distances) < len(nodes):
        # Some published SWCs include detached fragments. Animate each fragment
        # from its point nearest the soma; never invent a connecting segment.
        remaining = (node_id for node_id in nodes if node_id not in distances)
        root = min(remaining, key=lambda node_id: np.linalg.norm(np.subtract(nodes[node_id], soma_position)))
        distances[root] = float(np.linalg.norm(np.subtract(nodes[root], soma_position)))
        stack = [root]
        while stack:
            current = stack.pop()
            for neighbor in neighbors[current]:
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + float(
                        np.linalg.norm(np.subtract(nodes[current], nodes[neighbor]))
                    )
                    stack.append(neighbor)

    brain_links = [
        (child, parent)
        for child, parent in links
        if parent in nodes
        and nodes[child][2] < BRAIN_Z_LIMIT
        and nodes[parent][2] < BRAIN_Z_LIMIT
    ]
    if not brain_links:
        raise ValueError(f"No brain-space skeleton segments in {path}")
    segments = np.asarray([(nodes[child], nodes[parent]) for child, parent in brain_links], dtype=np.float32)
    path_distances = np.asarray(
        [(distances[child], distances[parent]) for child, parent in brain_links], dtype=np.float32
    )
    maximum = float(path_distances.max())
    if maximum <= 0:
        raise ValueError(f"No nonzero branch length in {path}")

    # One continuous branch gives the viewer a clearly visible travelling
    # spark. Restrict it to real brain-space links, including on fragmented SWCs.
    brain_neighbors: dict[int, list[int]] = {}
    for child, parent in brain_links:
        brain_neighbors.setdefault(child, []).append(parent)
        brain_neighbors.setdefault(parent, []).append(child)
    remaining = set(brain_neighbors)
    components: list[set[int]] = []
    while remaining:
        component = set()
        frontier = [remaining.pop()]
        while frontier:
            current = frontier.pop()
            component.add(current)
            for neighbor in brain_neighbors[current]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    frontier.append(neighbor)
        components.append(component)
    largest_component = max(components, key=len)
    branch_root = min(
        largest_component,
        key=lambda node_id: np.linalg.norm(np.subtract(nodes[node_id], soma_position)),
    )
    branch_lengths = {branch_root: 0.0}
    predecessors: dict[int, int | None] = {branch_root: None}
    stack = [branch_root]
    while stack:
        current = stack.pop()
        for neighbor in brain_neighbors[current]:
            if neighbor not in branch_lengths:
                branch_lengths[neighbor] = branch_lengths[current] + float(
                    np.linalg.norm(np.subtract(nodes[current], nodes[neighbor]))
                )
                predecessors[neighbor] = current
                stack.append(neighbor)
    tip = max(branch_lengths, key=branch_lengths.get)
    path_nodes = []
    while tip is not None:
        path_nodes.append(nodes[tip])
        tip = predecessors[tip]
    path_nodes.reverse()
    return segments, path_distances / maximum, np.asarray(path_nodes, dtype=np.float32)


def main() -> None:
    with np.load(DATA / "brain.npz") as brain:
        ids = brain["ids"]
        positions = brain["positions"]
        cell_types = brain["cell_type"]
        sides = brain["side"]
        total_neurons = len(ids)

    finite = np.isfinite(positions).all(axis=1)
    brain_mask = finite & (positions[:, 2] < BRAIN_Z_LIMIT)
    brain_positions = positions[brain_mask]
    bounds_min = brain_positions.min(axis=0)
    bounds_max = brain_positions.max(axis=0)
    center = (bounds_min + bounds_max) / 2
    scale = 7.2 / float(bounds_max[0] - bounds_min[0])

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "skeletons").mkdir(exist_ok=True)
    (OUTPUT / "populations").mkdir(exist_ok=True)
    transform(brain_positions, center, scale).tofile(OUTPUT / "brain-positions.bin")

    population_groups = []
    for name, cell_type, side, color in INPUT_POPULATIONS:
        members = (cell_types == cell_type) & (sides == side)
        positioned = members & brain_mask
        if not np.any(positioned):
            raise ValueError(f"No mapped positions for {cell_type}_{side}")
        file = f"populations/{name}.bin"
        transform(positions[positioned], center, scale).tofile(OUTPUT / file)
        population_groups.append({
            "name": name,
            "label": f"{cell_type}_{side}",
            "color": color,
            "neuron_count": int(members.sum()),
            "point_count": int(positioned.sum()),
            "file": file,
        })

    skeletons = []
    for body_id, label, role, color in BODY_IDS:
        matches = np.flatnonzero(ids == body_id)
        if len(matches) != 1 or not finite[matches[0]]:
            raise ValueError(f"Body ID {body_id} is missing a known soma position")
        segments, distances, surge_path = parse_swc(SOURCE / f"{body_id}.swc", positions[matches[0]])
        transformed = transform(segments.reshape(-1, 3), center, scale)
        transformed.tofile(OUTPUT / "skeletons" / f"{body_id}.bin")
        distances.astype("<f4").tofile(OUTPUT / "skeletons" / f"{body_id}-distance.bin")
        path_length = np.linalg.norm(np.diff(surge_path, axis=0), axis=1)
        path_progress = np.r_[0, np.cumsum(path_length)]
        if path_progress[-1] <= 0:
            raise ValueError(f"No continuous surge path in {body_id}.swc")
        path_data = np.column_stack((
            transform(surge_path, center, scale), path_progress / path_progress[-1]
        )).astype("<f4")
        path_data.tofile(OUTPUT / "skeletons" / f"{body_id}-surge.bin")
        soma = transform(positions[matches].copy(), center, scale)[0]
        skeletons.append({
            "body_id": body_id,
            "label": label,
            "role": role,
            "color": color,
            "soma": [round(float(value), 5) for value in soma],
            "segment_count": len(segments),
            "file": f"skeletons/{body_id}.bin",
            "distance_file": f"skeletons/{body_id}-distance.bin",
            "distance_origin": "nearest node to annotated soma per connected fragment; normalized branch path length",
            "surge_path_file": f"skeletons/{body_id}-surge.bin",
            "surge_path_point_count": len(surge_path),
            "surge_path_origin": "largest continuous brain-space fragment, from its node nearest annotated soma",
            "source": f"{SKELETON_SOURCE}{body_id}.swc",
        })

    manifest = {
        "dataset": "MaleCNS v1.0",
        "attribution": "FlyEM / HHMI Janelia, University of Cambridge, MRC Laboratory of Molecular Biology, Google Research",
        "license": "CC BY 4.0",
        "source": "https://male-cns.janelia.org/download/",
        "overview": {
            "file": "brain-positions.bin",
            "point_count": int(len(brain_positions)),
            "all_neuron_count": total_neurons,
            "positioned_neuron_count": int(finite.sum()),
            "region": "brain (soma or soma-tract points; z < 50,000 EM voxels)",
        },
        "population_groups": population_groups,
        "skeletons": skeletons,
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Exported {len(brain_positions):,} real brain positions and {len(skeletons)} real skeletons")


if __name__ == "__main__":
    main()
