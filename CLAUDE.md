# AI Game Development Agent Rules (Godot 4.x)

This document defines how the AI agent must work when developing this Godot project. Follow these rules strictly.

---

## 1. Execution Model

When receiving a request:

1. **Create a detailed internal plan** — determine which scenes, scripts, and resources must be created or modified. Verify feasibility.
2. **Implement everything autonomously** — never delegate work back to the user.
3. **Verify the project** — the task is NOT complete until verification passes.

### Verification

```bash
python3 godot-skills/godot_verify.py
```

Must finish with **0 errors, 0 warnings**. If issues appear: analyze → find root cause → fix → re-verify.

### Runtime Inspection

When logs are insufficient or would create spam:

```bash
python3 godot-skills/godot_execute.py $'var node = scene.find_child("Player")\nreturn {"pos": str(node.position)}'
```

### Documentation Lookup

When unsure about Godot API:

```bash
python3 godot-skills/godot_doc.py "CharacterBody3D"
```

---

## 2. Root Cause Fixing

Never fix only symptoms. Always:

1. Identify the root cause
2. Fix the underlying problem
3. Document findings in `godot-skills/EXPERIENCE.md`

---

## 3. Scene Architecture

### Scenes must be modular

Complex objects must be split into multiple scenes:

```
Player.tscn
└── Weapon.tscn
```

### Definition of Complex Scene

A scene is **complex** if:
- It contains **more than 100 nodes**
- It contains **deep or complicated branching**
- It becomes **cognitively difficult to understand**

Complex scenes must be split into smaller sub-scenes.

### Geometry

Never construct complex scene geometry from code. Instead:
- Create nodes and save them in `.tscn`
- Instantiate scenes when needed

---

## 4. Code Architecture

### One File = One Class

Each `.gd` file must define exactly one class.

### Script Structure (mandatory order)

1. `@tool` / `extends` / `class_name`
2. Signals
3. Enums
4. Constants
5. `@export` variables
6. Public variables
7. Private variables (prefixed `_`)
8. Lifecycle methods (`_ready`, `_process`, `_physics_process`, `_input`)
9. Public methods
10. Private methods (prefixed `_`)

### Size Limits

- Maximum **300 lines** per script — split into multiple scripts if needed
- Maximum **50 lines** per function — refactor into smaller functions if needed

### `class_name` is mandatory

Every script must declare a global class:

```gdscript
class_name Player
extends CharacterBody3D
```

### Static typing is required

```gdscript
var health: int = 100
func take_damage(amount: int) -> void:
```

### Exported variables

Use `@export` for ALL tunable parameters — no hardcoded gameplay values:

```gdscript
@export var speed: float = 200.0
@export var bullet_scene: PackedScene
@export var weapon: Weapon
```

### `@onready` is forbidden

Do not use `@onready`. Node references must be provided through `@export` and wired in `.tscn`:

```gdscript
@export var player: Player
```

### `$NodePath` is forbidden

Do not use `$NodePath` or `get_node()` with hardcoded paths. Use `@export` instead.

### Properties (avoid recursive setters)

```gdscript
var _hp: int = 100

var hp: int:
    get:
        return _hp
    set(value):
        _hp = clamp(value, 0, 100)
```

---

## 5. Error Safety

Always validate references before using them:

```gdscript
if not bullet_scene:
    push_error("Bullet scene not assigned")
    return
```

Never assume exported references are assigned.

---

## 6. Code Style

- Tabs for indentation
- Max line length: 80 characters
- Blank lines between logical sections
- Trailing commas in multiline arrays/dictionaries
- snake_case → variables, functions, signals
- PascalCase → classes, nodes
- ALL_CAPS → constants
- Prefix private variables and methods with `_`
- Virtual/override methods also start with `_`
- Prefer early returns over deep nesting
- Keep functions short and focused

---

## 7. Scene Files (.tscn)

A `.tscn` file has five sections in order:

1. **File descriptor**: `[gd_scene format=3 uid="uid://..."]` — `load_steps` is deprecated
2. **External resources**: `[ext_resource type="Script" path="res://..." id="1"]`
3. **Internal resources**: `[sub_resource type="BoxShape3D" id="BoxShape3D_abc"]` — referenced before referencing
4. **Nodes**: exactly one root node (no `parent=`), children use `parent="."` or deeper paths excluding root name
5. **Signal connections**: `[connection signal="..." from="..." to="." method="..."]`

`unique_id` field only exists in Godot 4.6+. Do not assume it always exists.

---

## 8. Resource Files (.tres)

```
[gd_resource type="StandardMaterial3D" format=3 uid="uid://..."]

[resource]
albedo_color = Color(0.8, 0.2, 0.1, 1)
```

**CRITICAL**: The `[resource]` section is mandatory. Without it, Godot fails to parse.

---

## 9. Completion Criteria

A task is complete ONLY when:

- [ ] All required scenes/scripts exist
- [ ] Project verification passes (0 errors, 0 warnings)
- [ ] Architecture rules are respected
- [ ] Root causes were addressed
- [ ] Experience entries recorded in `godot-skills/EXPERIENCE.md` if needed
