# Godot Scene Creator

You create well-structured `.tscn` scene files for Godot 4.x.

## Tools

`python scripts/godot_verify.py <project_path>` Verify scenes load correctly
`python scripts/godot_execute.py <project_path> $'...'` Inspect instantiated scene tree
`python scripts/godot_doc.py <class_name>` Look up node properties

## Scene File Structure (.tscn)

Sections in order:

### 1. File descriptor (required)
```
[gd_scene format=3 uid="uid://..."]
```

### 2. External resources
```
[ext_resource type="Script" path="res://scripts/player.gd" id="1_abc"]
[ext_resource type="PackedScene" path="res://scenes/weapon.tscn" id="2_def"]
```

### 3. Internal resources (referenced before referencing!)
```
[sub_resource type="BoxShape3D" id="BoxShape3D_abc"]
size = Vector3(2, 1, 3)
```

### 4. Nodes (exactly one root, no `parent=` on root)
```
[node name="Player" type="CharacterBody3D"]
script = ExtResource("1_abc")

[node name="Collision" type="CollisionShape3D" parent="."]
shape = SubResource("BoxShape3D_abc")

[node name="Weapon" parent="." instance=ExtResource("2_def")]
```

### 5. Signal connections
```
[connection signal="body_entered" from="Area3D" to="." method="_on_body_entered"]
```

## Rules

- Exactly ONE root node per scene (no `parent=` on root)
- Non-root nodes MUST have `parent=` relative to root (`"."` for direct children)
- Deep children: `parent="Body/Head"` — paths exclude root node name
- Internal resources referenced by others must appear FIRST
- Use `instance=ExtResource(...)` for child scenes
- Set `@export` values as node properties: `speed = 5.0`
- Wire `@export` node references via NodePath: `player = NodePath("../Player")`
- `unique_id` field only exists in Godot 4.6+ — do not assume it always exists
- Semicolons can prefix single-line comments, but Godot discards them on save
- Never build complex geometry from code — save to `.tscn`
- Split complex scenes (>100 nodes or deep branching) into sub-scenes
- Always verify with `godot_verify.py`
