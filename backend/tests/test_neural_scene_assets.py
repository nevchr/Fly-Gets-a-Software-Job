"""The small browser assets must stay aligned with the simulated cell IDs."""

import json
from pathlib import Path

import numpy as np

from app.simulator.brain.fly_connectome import VISUAL_BODY_IDS


DATA = Path(__file__).resolve().parents[2] / "frontend" / "public" / "data" / "malecns"


def test_neural_scene_assets_match_manifest():
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    overview = manifest["overview"]
    assert overview["point_count"] == 125_020
    assert (DATA / overview["file"]).stat().st_size == overview["point_count"] * 3 * 4
    assert [item["body_id"] for item in manifest["skeletons"]] == list(VISUAL_BODY_IDS)
    assert [item["name"] for item in manifest["population_groups"]] == [
        "approach", "avoidance", "threat", "looming_work", "choice_uncertainty",
    ]
    assert sum(item["point_count"] for item in manifest["population_groups"]) == 489
    for population in manifest["population_groups"]:
        assert (DATA / population["file"]).stat().st_size == population["point_count"] * 3 * 4
    for skeleton in manifest["skeletons"]:
        assert (DATA / skeleton["file"]).stat().st_size == skeleton["segment_count"] * 2 * 3 * 4
        segments = np.fromfile(DATA / skeleton["file"], dtype="<f4").reshape(-1, 2, 3)
        distances = np.fromfile(DATA / skeleton["distance_file"], dtype="<f4")
        assert len(distances) == skeleton["segment_count"] * 2
        assert np.isfinite(distances).all()
        assert distances.min() >= 0
        assert distances.max() == 1
        surge_path = np.fromfile(DATA / skeleton["surge_path_file"], dtype="<f4").reshape(-1, 4)
        assert len(surge_path) == skeleton["surge_path_point_count"]
        assert np.isfinite(surge_path).all()
        assert surge_path[0, 3] == 0
        assert surge_path[-1, 3] == 1
        assert np.all(np.diff(surge_path[:, 3]) > 0)
        real_edges = {
            frozenset((tuple(segment[0]), tuple(segment[1])))
            for segment in segments
        }
        assert all(
            frozenset((tuple(start), tuple(end))) in real_edges
            for start, end in zip(surge_path[:-1, :3], surge_path[1:, :3])
        )
