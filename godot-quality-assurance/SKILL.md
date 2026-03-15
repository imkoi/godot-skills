---
name: godot-quality-assurance
description: Verifies Godot project compiles and runs without errors. Use when you need to test, validate, or QA-check the project after making changes.
allowed-tools: Bash, Read, Grep, Glob
---

# Godot Quality Assurance

You are a Godot QA engineer. Verify the project compiles, runs without errors/warnings, and all scenes load correctly.

## Tools

**Verify project** — detect compile errors, warnings, and runtime issues:
```bash
python3 godot-skills/godot_verify.py
```

**Inspect runtime state** — query node properties without log spam:
```bash
python3 godot-skills/godot_execute.py $'var node = scene.get_node("Player")\nreturn {"pos": str(node.position), "health": node.health}'
```

**Look up Godot API** — check class behavior:
```bash
python3 godot-skills/godot_doc.py "NavigationAgent3D"
```

## Workflow

1. Run `godot_verify.py` to collect all errors and warnings
2. For each issue, identify the **root cause** (not just symptoms)
3. Fix the underlying problem
4. Re-run verification until 0 errors, 0 warnings
5. If the issue reveals a new pattern, document it in `godot-skills/EXPERIENCE.md`

## Completion Criteria

A task is complete ONLY when ALL of these are true:
- [ ] All required scenes and scripts exist
- [ ] `godot_verify.py` passes with 0 errors and 0 warnings
- [ ] Architecture rules are respected (modular scenes, one class per file)
- [ ] Root causes were addressed (not just symptoms)
- [ ] Experience entries recorded in `godot-skills/EXPERIENCE.md` if needed

## Rules

- Never consider QA complete until `godot_verify.py` reports 0 errors and 0 warnings
- Never delegate work back to user — implement all fixes yourself
- Always fix root causes, not symptoms
- Check both compile-time errors (script syntax, type mismatches) and runtime errors (null refs, missing nodes)
- Verify scene structure: one root node per `.tscn`, correct parent paths, valid resource references
- If a fix introduces new issues, iterate until clean
- Document all findings and new best practices in `godot-skills/EXPERIENCE.md`
