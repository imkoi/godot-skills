---
name: godot-resource-creator
description: Creates Godot .tres resource files — materials, shapes, themes, custom resources. Use when creating standalone resource files for materials, collision shapes, curves, or custom data assets.
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# Godot Resource Creator

You create `.tres` resource files for Godot 4.x — materials, shapes, curves, custom resources, themes, and data assets.

## Tools

```bash
python3 godot-skills/godot_verify.py                        # Verify resources load
python3 godot-skills/godot_execute.py $'...'                 # Inspect resources at runtime
python3 godot-skills/godot_doc.py "StandardMaterial3D"       # Look up resource properties
```

## Resource File Structure (.tres)

### 1. File descriptor (required)
```
[gd_resource type="StandardMaterial3D" format=3 uid="uid://..."]
```

### 2. External resources (optional)
```
[ext_resource type="Texture2D" path="res://textures/albedo.png" id="1_abc"]
```

### 3. Sub-resources (optional, order matters)
```
[sub_resource type="Gradient" id="Gradient_abc"]
colors = PackedColorArray(1, 0, 0, 1, 0, 0, 1, 1)
```

### 4. Resource section (REQUIRED)
```
[resource]
albedo_color = Color(0.8, 0.2, 0.1, 1)
```

**CRITICAL**: The `[resource]` section is mandatory. Without it, Godot fails to parse.

## Examples

**Material:**
```tres
[gd_resource type="StandardMaterial3D" format=3]

[resource]
albedo_color = Color(0.5, 0.7, 0.3, 1)
metallic = 0.2
roughness = 0.8
```

**Custom Resource:**
```tres
[gd_resource type="Resource" script_class="WeaponData" format=3]

[ext_resource type="Script" path="res://scripts/weapon_data.gd" id="1_script"]

[resource]
script = ExtResource("1_script")
damage = 25
fire_rate = 0.3
```

## Rules

- Always include the `[resource]` section — omitting it causes "Failed loading resource" / "Unexpected end of file"
- `type` in descriptor must match Godot class name exactly
- Sub-resources referenced by others must appear FIRST
- For custom resources, the script must exist with `class_name` before `.tres` references it
- Always validate `PackedScene` references before calling `instantiate()` — use `if not scene: push_error(...); return`
- Use `read` to verify structure of existing resources before creating similar files
- Always verify with `godot_verify.py`
- Document findings in `godot-skills/EXPERIENCE.md` if issues arise
