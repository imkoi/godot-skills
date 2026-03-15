Ниже — переработанная структура.
# AI Game Development Agent Rules (Godot)

This document defines how the AI agent must work when developing a Godot
project. The agent must strictly follow these rules.

---

# 1. Execution Model

When receiving a request, the agent must follow this workflow:

1. **Create a detailed internal plan**
   - Determine which scenes, scripts, and resources must be created or modified.
   - Verify that the plan is technically feasible.

2. **Implement everything autonomously**
   - The agent must perform all required implementation steps.
   - Never delegate work back to the user.

   Example of forbidden behavior:

   ❌ "I implemented the system. Now create a scene and add this script."

   Correct behavior:

   ✅ The agent creates the scene, script, nodes, and configuration itself.

3. **Verify the project**

The project **must always be verified** using:

```

python3 playmaker/godot_verify.py

```

Example successful output:

```

Scanning project with 4 scenes...
Verification finished with 0 errors, 0 warnings

```

If errors or warnings appear:

- analyze logs
- identify root cause
- fix the problem
- run verification again

The task **must not be considered complete** until verification passes with
zero errors and zero warnings.

---

# 2. Root Cause Fixing

The agent must **never fix only symptoms**.

Instead:

1. identify the root cause
2. fix the underlying problem
3. document findings in:

```

playmaker/EXPERIENCE.md

```

Example entry:

```

## Script Errors & Scene Instantiation

Problem:
"Cannot call method 'instantiate' on a null value"

Root Cause:
PackedScene variables were exported but not assigned in the .tscn file.

Best Practice:
Always validate exported PackedScene references before calling instantiate().
Use defensive checks and push_error() for missing assignments.

```

This file acts as a **long-term knowledge base** for future development.

---

# 3. Scene Architecture Rules

Godot scenes must follow these principles.

### Scenes must be modular

Complex objects must be split into multiple scenes.

Example:

```

Player.tscn
└ Weapon.tscn

````

Do not build complex objects entirely inside one scene.

---

### Definition of a Complex Scene

A scene is considered **complex** if:

- it contains **more than 100 nodes**
- it contains **deep or complicated branching**
- it becomes **cognitively difficult to understand**

Complex scenes must be split into smaller scenes.

---

### Geometry and scene structure

Never construct complex scene geometry purely from code.

Instead:

- create nodes
- save them in `.tscn`
- instantiate scenes when needed

---

# 4. Code Architecture Rules

Every script must follow these rules.

### One File = One Class

Each `.gd` file must define exactly one class.

---

### `class_name` is mandatory

Every script must declare a global class.

Example:

```gdscript
class_name Player
extends CharacterBody2D
````

---

### Static typing is required

Always prefer typed variables.

```gdscript
var health: int = 100
```

---

### Exported variables

Use `@export` for:

* tunable gameplay parameters
* scene references
* PackedScene references
* any value that would otherwise be hardcoded

Example:

```gdscript
@export var speed: float = 200.0
@export var bullet_scene: PackedScene
@export var weapon: Weapon
```

---

### Hardcoded values are forbidden

Instead of:

```
var speed = 200
```

Use:

```
@export var speed: float = 200.0
```

This allows designers to tune gameplay.

---

### `@onready` is forbidden

Do not use `@onready`.

Node references must be provided through:

* exported variables
* scene wiring

Example:

```
@export var player: Player
```

---

# 5. Error Safety

Always validate references before using them.

Example:

```gdscript
if not bullet_scene:
	push_error("Bullet scene not assigned")
	return
```

Never assume exported references are assigned.

---

# 6. Project Editing Rules

The agent works directly with Godot text resources.

Allowed formats:

```
.gd
.tscn
.tres
```

All edits must follow the official scene format rules.

---

# 7. Logging & Runtime Inspection

If behavior cannot be verified through logs:

Use runtime inspection tools.

```
python3 playmaker/godot_execute.py $'script'
```

This script can:

* find nodes
* inspect properties
* print values

Use this instead of adding log spam.

---

# 8. Documentation Lookup

To inspect Godot classes:

```
python3 playmaker/godot_doc.py "Node2D"
```

Use this whenever the agent is unsure about API behavior.

---

# 9. Completion Criteria

A task is complete only if:

✔ all required scenes/scripts exist
✔ project verification passes
✔ no warnings or errors remain
✔ architecture rules are respected
✔ root causes were addressed
✔ experience entries were recorded if needed

````

---

# skills/gdscript.md

```md
# Skill: Writing GDScript

Every script must follow the structure below.

---

# Script Layout

Order of sections:

1. tool / extends / class_name
2. signals
3. enums
4. constants
5. exported variables
6. public variables
7. private variables
8. lifecycle methods
9. public methods
10. private methods

---

# Example Script

```gdscript
class_name Player
extends CharacterBody2D


signal health_changed(new_health: int)


enum WeaponType {
	PISTOL,
	RIFLE,
	SHOTGUN,
}


const MAX_HEALTH: int = 100


@export var speed: float = 200.0
@export var weapon: Weapon


var health: int = MAX_HEALTH


func _ready() -> void:
	pass


func take_damage(amount: int) -> void:

	health = clamp(health - amount, 0, MAX_HEALTH)
	health_changed.emit(health)


func is_dead() -> bool:
	return health <= 0
````

---

# Property Example (Correct Implementation)

Avoid recursive setters.

Correct pattern:

```gdscript
var _hp: int = 100

var hp: int:
	get:
		return _hp
	set(value):
		_hp = clamp(value, 0, 100)
```

---

# Naming Conventions

snake_case → variables and functions
PascalCase → classes, nodes
ALL_CAPS → constants

---

# Code Style

* tabs for indentation
* max line length: 80 characters
* blank lines between logical sections
* early returns preferred
* short focused functions

````

---

# skills/scenes.md

```md
# Skill: Godot Scene Files (.tscn)

Godot uses text based scene files.

A `.tscn` file has these sections:

1. file descriptor
2. external resources
3. internal resources
4. nodes
5. signal connections

---

# Scene Descriptor

Example:

````

[gd_scene format=3 uid="uid://example"]

```

---

# Nodes

The first node is the root.

Example:

```

[node name="Player" type="CharacterBody2D"]

```

Children reference parents:

```

[node name="Camera2D" type="Camera2D" parent="."]

```

---

# Resources

External:

```

[ext_resource type="Script" path="res://player/player.gd" id="1"]

```

Internal:

```

[sub_resource type="SphereMesh" id="SphereMesh_123"]

```

---

# Important Rules

A valid scene must contain:

- exactly **one root node**

Parent paths must:

- be relative to the root
- exclude the root name
```

---

# skills/architecture.md

```md
# Skill: Game Architecture

Large gameplay systems must be separated into scenes.

Example:

```

Player
├ CharacterBody2D
├ Camera
├ Weapon (child scene)

```

Advantages:

- reusable scenes
- easier debugging
- simpler mental model
```

---

# playmaker/EXPERIENCE.md (example)

```md
# Development Experience Log

This document records important findings.

Each entry must include:

- problem
- root cause
- best practice

---

## Script Errors & Scene Instantiation

Problem:
"Cannot call method 'instantiate' on a null value"

Root Cause:
PackedScene variables were exported but not assigned in .tscn files.

Best Practice:
Always validate exported PackedScene references before calling
instantiate(). Use push_error() to detect missing assignments early.

---

## Missing Scene References

Problem:
Runtime crash due to missing node reference.

Root Cause:
Exported variable was not assigned in the scene.

Best Practice:
Always validate exported references in `_ready()` and provide
clear push_error messages.
```