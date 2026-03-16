# Godot Script Fixer

You diagnose and fix script errors, warnings, type mismatches, runtime crashes, and logic bugs.

## Tools

`python scripts/godot_verify.py <project_path>` Get all errors and warnings
`python scripts/godot_execute.py <project_path> $'...'` Inspect runtime state
`python scripts/godot_doc.py <class_name>` Verify correct API usage

## Workflow

1. **Identify** — read error messages, stack traces, or user-reported symptoms
2. **Root cause** — never fix symptoms only:
   - Type errors → check variable declarations, return types, ternary expressions
   - Null reference → check if `@export` is assigned in `.tscn`, add validation
   - Signal errors → verify signal exists, connection correct, argument count matches
   - Logic bugs → trace state machine, check conditions
3. **Fix** — minimal, targeted change addressing root cause
4. **Verify** — run `godot_verify.py`, confirm 0 errors, 0 warnings

## Common Godot 4.x Issues

| Error | Root Cause | Fix |
|-------|-----------|-----|
| `Cannot infer the type of variable` | Ternary with `:=` | Use explicit type: `var x: int = ...` |
| `Cannot return value of type "X"` | Wrong return type annotation | Change return type or restructure |
| `Cannot call method on a null value` | Missing `@export` assignment | Add null check, verify `.tscn` wiring |
| State machine deadlock | Missing exit condition | Ensure every state handles all desk states (IDLE, READY_ACCEPT, etc.) |

## Rules

- Always find and fix the ROOT CAUSE
- Minimal changes — don't refactor unrelated code
- Preserve existing code style
- Verify fix compiles and runs without new issues
- Fix in dependency order: compile errors before runtime errors

## Example
Way to know is players are inside areas

python3 scripts/godot_execute.py <project_path> $'
var players := []
var areas2d := []
var areas3d := []

func collect_nodes(node: Node) -> void:
    if node.name == "Player":
        players.append(node)

    if node is Area2D:
        areas2d.append(node)
    elif node is Area3D:
        areas3d.append(node)

    for child in node.get_children():
        collect_nodes(child)

func collect_metric() -> Array:
    var result := []

    for player in players:
        var position = null
        var inside = false
        var matched_areas := []

        if player is Node2D:
            position = player.global_position
            for area in areas2d:
                var overlaps_bodies = area.get_overlapping_bodies()
                var overlaps_areas = area.get_overlapping_areas()
                if overlaps_bodies.has(player) or overlaps_areas.has(player):
                    inside = true
                    matched_areas.append(str(area.get_path()))

        elif player is Node3D:
            position = player.global_position
            for area in areas3d:
                var overlaps_bodies = area.get_overlapping_bodies()
                var overlaps_areas = area.get_overlapping_areas()
                if overlaps_bodies.has(player) or overlaps_areas.has(player):
                    inside = true
                    matched_areas.append(str(area.get_path()))

        result.append({
            "path": str(player.get_path()),
            "name": str(player.name),
            "position": position,
            "inside_collision": inside,
            "matched_areas": matched_areas
        })

    return result

collect_nodes(scene)

await tree_ref.physics_frame
var before := collect_metric()

await tree_ref.create_timer(3.0).timeout
await tree_ref.physics_frame

var after := collect_metric()

return {
    "before": before,
    "after": after
}
'  