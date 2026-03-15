# Experience Log: Godot Development Best Practices

## 1. Resource Management & Loading
- **Problem**: Encountered "Failed loading resource" and "Unexpected end of file" errors when manually creating `.tres` files.
- **Root Cause**: Manually written `.tres` files lacked the `[resource]` header section required by Godot's resource loader, leading to parsing failures.
- **Best Practice**: Always include the `[resource]` header in manual resource files. Use `read` to verify the structure of existing resources before creating or modifying similar files.

## 2. Script Errors & Scene Instantiation
- **Problem**: "Cannot call method 'instantiate' on a null value" during `godot_verify.py` execution.
- **Root Cause**: `PackedScene` variables were declared in scripts but not assigned in the `.tscn` files, resulting in null references at runtime.
- **Best Practice**: Always check for null references before calling methods like `instantiate()` on exported `PackedScene` variables. Add defensive checks (`if not variable: push_error(...)`) to catch missing assignments early.

## 3. Scene Editing & Tooling
- **Problem**: `patch` tool failed due to "File may have changed externally" or "File already exists".
- **Root Cause**: Over-reliance on memory-based editing without ensuring the local file state matched the expected `old_string`. Also, failing to use `overwrite: true` when creating resources that already existed.
- **Best Practice**: Always use `read` immediately before a `patch` or `write` operation to ensure the local file content matches the `old_string` and to check for existing file conflicts.

## 4. Animation Setup
- **Problem**: `Condition "p_animation.is_null()" is true` errors during scene verification.
- **Root Cause**: Incorrect manual definition of `AnimationLibrary` and nested `Animation` data structure in `.tscn` files.
- **Best Practice**: Define `Animation` resources separately and reference them within the `AnimationLibrary`. Follow the standard Godot text-based scene format precisely for animations.