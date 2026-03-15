# Mindset
- When you receive user reqeuset - make a detailed plan what should be implemented and verify this plan
- You never ask user to implement something, instead you doing everything by yourself
- When you complete task verify that all steps are completed, never provide task that have some uncompleted steps
- Never complete task until you tested, checked all logs, fixed errors and warning. To test and get info use python3 godot_verify.py
- You not fixing unique cases, you are finding root cause and write your findings and how to in godot-playmaker/EXPERIENCE.md
- If you need godot specific functions - configure project settings or create node or change property in resources PLEASE remember that you work in godot and all files have text based format, in this document below you will find instructions how to create and manage scenes, resources, gdscripts in text
- Never hardcode variables, make as much @export variables in script as you can to let game designer setup the game feel.
- Never build complex scenes/geometry from code, instead it should be saved to .tscn file.
- Split your object to nodes and save them in .tscn, if Scene is complex for example player who has weapon - split player and weapon to different scenes, where player will contains weapon scene inside
- If you are verifying behaviour and logs is not enough, or logs could create log spam - use script execution through python3 godot-playmaker/godot_execute.py $'your script' and in this script just find nodes, in nodes you can inspect and log specific variables
- If you need to get doc regarding specific node or type - use python3 godot-playmaker/godot_doc.py "Node2D" 


## GDSCRIPT
When generating GDScript:
1. Always specify `extends`.
2. Prefer static typing.
3. Use `@export` for tunable parameters.
4. Use signals for event communication.
5. Use `@onready` for node references.
6. Always register script global class name
7. Dont preload nodes or reference them thorugh $NodePath, instead make @export var myPlayer: Player and set player in .tscn

1. **Script defines behavior for a node and usually extends an engine class. Also the class than inherit this node should be specified**
```gdscript
class_name Player
extends CharacterBody2D
```
2. **Variables are declared using `var` and static typing.**
```gdscript
var health: int = 100
```
3. **Constants use `const`.**
```gdscript
const MAX_SPEED: int = 200
```
4. **Functions should be static typed and can define typed parameters and return types.**
```gdscript
func add(a: int, b: int) -> int:
    return a + b
```
5. **Control flow supports `if / elif / else`.**
```gdscript
if health <= 0:
    print("Dead")
elif health < 50:
    print("Low health")
else:
    print("Healthy")
```
6. **Loops include `for` iteration over collections.**
```gdscript
for i in range(3):
    print(i)
```
7. **`while` loops are supported.**
```gdscript
var i = 0
while i < 5:
    print(i)
    i += 1
```
8. **Enums define grouped integer constants.**
```gdscript
enum WeaponType { PISTOL, RIFLE, SHOTGUN }
```
9. **Signals allow event-based communication.**
```gdscript
signal health_changed(new_health)
```
10. **Signals are emitted with `emit`.**
```gdscript
health_changed.emit(health)
```
11. **Variables can be exposed to the editor with `@export`.**
```gdscript
@export var speed: float = 250
```
12. **Scripts can run in the editor using `@tool`.**
```gdscript
@tool
extends Node
```
13. **Properties can use getters and setters.**
```gdscript
var hp: int:
    set(value):
        hp = clamp(value, 0, 100)
```
14. **Match statements provide pattern-based branching.**
```gdscript
match weapon:
    WeaponType.PISTOL:
        shoot_pistol()
    WeaponType.RIFLE:
        shoot_rifle()
```
15. **Inner classes can be defined inside scripts.**
```gdscript
class Weapon:
    var damage: int = 10
```
16. **Abstract classes can be declared. Abstract methods must be implemented in subclasses.**
```gdscript
@abstract
class_name Character

@abstract func attack() -> void:
```
17. **Inheritance is supported with `extends`. Subclasses implement required abstract methods.**
```gdscript
class_name Enemy
extends Character

func attack() -> void:
    print("Enemy attack")
```


## Create Scenes and Resouces
1. `TSCN` is Godot’s text-based scene format representing a single scene tree.
2. It is human-readable and version-control friendly compared to binary scene formats.
3. A `.tscn` file has five main sections: file descriptor, external resources, internal resources, nodes, and connections.
4. The first entry must be the file descriptor, e.g. `[gd_scene format=3 uid="uid://..."]`.
5. Older scenes may include `load_steps=<int>` in the descriptor; this is deprecated and should be ignored.
6. Each section is composed of bracketed headings plus optional `key = value` property lines below them.
7. Valid entry heading types include `ext_resource`, `sub_resource`, `node`, and `connection`.
8. Entry syntax is generally `[entry_type key=value key=value ...]`.
9. Property values may be primitive or complex Godot datatypes such as arrays, transforms, colors, and packed arrays.
10. `ext_resource` defines a reference to a resource stored outside the scene file.
11. External resources typically include `type`, `uid`, `path`, and `id`.
12. Godot usually writes external paths as `res://...`, though relative paths are also valid.
13. `sub_resource` defines a resource embedded inside the `.tscn` file itself.
14. Internal resources are used for embedded data such as shapes, materials, meshes, animations, and similar scene-owned assets.
15. Order matters for internal resources: if one internal resource references another, the referred resource must appear first.
16. `node` entries define the actual scene tree structure.
17. A node header typically contains `name`, `type`, `parent`, and sometimes `unique_id`.
18. `unique_id` is only present in scenes saved with Godot 4.6 or later, so parsers must not assume it always exists.
19. The first `node` entry is the scene root and must not contain a `parent=` field.
20. A valid scene file must have exactly one root node; otherwise import fails. 
21. For non-root nodes, parent paths are absolute relative paths inside the scene tree, excluding the root node’s own name.
22. If a node is a direct child of the root, its parent path should be `"."`.
23. `connection` entries serialize signal connections between nodes.
24. Semicolon-prefixed single-line comments are allowed in text resources, but Godot discards comments and extra whitespace when saving.

```.tscn
[gd_scene format=3 uid="uid://cecaux1sm7mo0"]

[sub_resource type="SphereShape3D" id="SphereShape3D_tj6p1"]

[sub_resource type="SphereMesh" id="SphereMesh_4w3ye"]

[sub_resource type="StandardMaterial3D" id="StandardMaterial3D_k54se"]
albedo_color = Color(1, 0.639216, 0.309804, 1)

[node name="Ball" type="RigidBody3D" unique_id=1358867382]

[node name="CollisionShape3D" type="CollisionShape3D" parent="." unique_id=1279975976]
shape = SubResource("SphereShape3D_tj6p1")

[node name="MeshInstance3D" type="MeshInstance3D" parent="." unique_id=558852834]
mesh = SubResource("SphereMesh_4w3ye")
surface_material_override/0 = SubResource("StandardMaterial3D_k54se")

[node name="OmniLight3D" type="OmniLight3D" parent="." unique_id=1581292810]
light_color = Color(1, 0.698039, 0.321569, 1)
omni_range = 10.0

[node name="Camera3D" type="Camera3D" parent="." unique_id=795715540]
transform = Transform3D(1, 0, 0, 0, 0.939693, 0.34202, 0, -0.34202, 0.939693, 0, 1, 3)
```

```.tres
[gd_resource type="ArrayMesh" format=3 uid="uid://dww8o7hsqrhx5"]

[ext_resource type="Material" path="res://player/model/playerobot.tres" id="1_r3bjq"]

[resource]
resource_name = "player_Sphere_016"
_surfaces = [{
"aabb": AABB(-0.207928, 1.21409, -0.14545, 0.415856, 0.226569, 0.223374),
"attribute_data": PackedByteArray(63, 121, ..., 117, 63),
"bone_aabbs": [AABB(0, 0, 0, -1, -1, -1), ..., AABB(-0.207928, 1.21409, -0.14545, 0.134291, 0.226569, 0.223374)],
"format": 7191,
"index_count": 1224,
"index_data": PackedByteArray(30, 0, ..., 150, 4),
"lods": [0.0382013, PackedByteArray(33, 1, ..., 150, 4)],
"material": ExtResource("1_r3bjq"),
"name": "playerobot",
"primitive": 3,
"skin_data": PackedByteArray(15, 0, ..., 0, 0),
"vertex_count": 1250,
"vertex_data": PackedByteArray(196, 169, ..., 11, 38)
}]
blend_shape_mode = 0
```


## Code Style
- Use indentation for blocks (no braces).
- Recommended line length: less or equal to 80 characters.
- Do not use hardcoded values, all hardcoded values should be stored in @export
- Use tabs for indentation.
- Add blank lines between logical code sections.
- Use snake_case for variables, functions, and signals.
- Use PascalCase for class names and types.
- Use ALL_CAPS for constants.
- Prefix private variables and methods with _.
- Virtual or override methods also start with _.
- Use explicit static typing where possible for readability and tooling.
- Prefer var name: Type = value syntax for typed variables.
- Group code in a consistent order inside scripts. Recommended script order: tool/extends/class_name → signals → enums → constants → exported variables → public vars → private vars → lifecycle methods → public methods → private methods.
- Exported properties should appear before internal variables.
- Use trailing commas in multiline arrays/dictionaries for cleaner diffs.
- Keep functions short and focused on a single responsibility.
- Use descriptive variable and function names.
- Prefer early returns instead of deep nesting.
- Code should remain self-descriptive.
- Maintain consistent formatting to support auto-formatters and linters.
