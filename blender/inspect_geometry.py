"""Report mesh islands and materials in the fly scene."""

import bpy


def islands(mesh):
    parent = list(range(len(mesh.vertices)))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for edge in mesh.edges:
        a, b = map(find, edge.vertices)
        parent[a] = b

    groups = {}
    for index, vertex in enumerate(mesh.vertices):
        groups.setdefault(find(index), []).append(vertex.co)
    return sorted(groups.values(), key=len, reverse=True)


for obj in bpy.data.objects:
    if obj.type not in {"MESH", "CURVE"}:
        continue
    print("OBJECT", obj.name, "materials", [m.name if m else None for m in obj.data.materials])
    if obj.type != "MESH":
        print("  splines", len(obj.data.splines))
        continue
    for group in islands(obj.data):
        world = [obj.matrix_world @ vertex for vertex in group]
        print(
            "  island", len(group),
            "min", tuple(round(min(p[axis] for p in world), 3) for axis in range(3)),
            "max", tuple(round(max(p[axis] for p in world), 3) for axis in range(3)),
        )

for material in bpy.data.materials:
    base = None
    if material.use_nodes:
        for node in material.node_tree.nodes:
            if node.type == "BSDF_PRINCIPLED":
                base = tuple(round(v, 3) for v in node.inputs["Base Color"].default_value)
    print("MATERIAL", material.name, "diffuse", tuple(round(v, 3) for v in material.diffuse_color), "base", base)
    if material.use_nodes:
        print("  NODES", [(node.name, node.type) for node in material.node_tree.nodes])
