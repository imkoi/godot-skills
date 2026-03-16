import argparse
import os
import re
import subprocess
import sys
import time
import uuid
import shutil


DEFAULT_PROJECT_PATH = r"/home/imkoi/gemini-test"


def find_godot() -> str:
    from_env = os.environ.get("GODOT_PATH")
    if from_env and os.path.isfile(from_env):
        return from_env

    for name in ["godot4", "godot", "Godot"]:
        found = shutil.which(name)
        if found:
            return found

    pattern = re.compile(r'(?:^|[;:])([^;:]*?[/\\](?:[Gg]odot)[^;:/\\]*)', re.IGNORECASE)
    candidates: list[str] = []
    for value in os.environ.values():
        for match in pattern.finditer(value):
            path = match.group(1).strip()
            if os.path.isfile(path):
                candidates.append(path)

    if len(candidates) == 1:
        return candidates[0]

    raise FileNotFoundError(
        "Godot not found. Set GODOT_PATH env var or add godot to PATH."
        + (f" (found multiple candidates: {candidates})" if len(candidates) > 1 else "")
    )


def read_main_scene(project_path: str) -> tuple[str | None, str | None]:
    project_file = os.path.join(project_path, "project.godot")
    if not os.path.isfile(project_file):
        return None, f"project.godot not found: {project_file}"

    with open(project_file, "r", encoding="utf-8") as f:
        text = f.read()

    patterns = [
        r'application/run/main_scene\s*=\s*"(.+?)"',
        r'run/main_scene\s*=\s*"(.+?)"',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            main_scene = match.group(1).strip()
            if not main_scene:
                return None, "Main scene is set in project.godot, but the value is empty."
            return main_scene, None

    return None, "Main scene is not set in project settings (project.godot)."


def indent_code(code: str, spaces: int = 4) -> str:
    pad = " " * spaces
    lines = code.splitlines()
    if not lines:
        return pad + "return null"
    return "\n".join(pad + line if line.strip() else "" for line in lines)


def resolve_script_arg(script_arg: str) -> str:
    if os.path.isfile(script_arg):
        with open(script_arg, "r", encoding="utf-8") as f:
            return f.read()
    return script_arg


def escape_gd_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_wrapper_script(main_scene_res: str, user_code: str) -> str:
    user_code_indented = indent_code(user_code, 4)
    escaped_scene = escape_gd_string(main_scene_res)

    return f'''extends SceneTree

var scene = null
var tree_ref = null
var root_node = null


func to_jsonable(value):
    if value == null:
        return null

    var t = typeof(value)

    match t:
        TYPE_BOOL, TYPE_INT, TYPE_FLOAT, TYPE_STRING:
            return value

        TYPE_VECTOR2:
            return {{
                "x": value.x,
                "y": value.y
            }}

        TYPE_VECTOR2I:
            return {{
                "x": value.x,
                "y": value.y
            }}

        TYPE_VECTOR3:
            return {{
                "x": value.x,
                "y": value.y,
                "z": value.z
            }}

        TYPE_VECTOR3I:
            return {{
                "x": value.x,
                "y": value.y,
                "z": value.z
            }}

        TYPE_VECTOR4:
            return {{
                "x": value.x,
                "y": value.y,
                "z": value.z,
                "w": value.w
            }}

        TYPE_VECTOR4I:
            return {{
                "x": value.x,
                "y": value.y,
                "z": value.z,
                "w": value.w
            }}

        TYPE_COLOR:
            return {{
                "r": value.r,
                "g": value.g,
                "b": value.b,
                "a": value.a
            }}

        TYPE_NODE_PATH:
            return str(value)

        TYPE_ARRAY:
            var arr := []
            for item in value:
                arr.append(to_jsonable(item))
            return arr

        TYPE_DICTIONARY:
            var dict := {{}}
            for key in value.keys():
                dict[str(key)] = to_jsonable(value[key])
            return dict

        TYPE_OBJECT:
            if value is Node:
                return {{
                    "__type": "Node",
                    "name": str(value.name),
                    "path": str(value.get_path())
                }}
            return str(value)

        _:
            return str(value)


func __user_main():
{user_code_indented}


func _initialize():
    tree_ref = self
    root_node = get_root()

    var packed = load("{escaped_scene}")
    if packed == null:
        push_error("[godot_execute] Failed to load main scene: {escaped_scene}")
        quit(2)
        return

    scene = packed.instantiate()
    if scene == null:
        push_error("[godot_execute] Failed to instantiate main scene: {escaped_scene}")
        quit(3)
        return

    root_node.add_child(scene)

    await process_frame
    await process_frame
    await physics_frame

    var result = await __user_main()
    var safe_result = to_jsonable(result)
    print(JSON.stringify(safe_result))

    quit(0)
'''


def make_temp_script(project_path: str, content: str) -> str:
    name = f"__godot_execute_{uuid.uuid4().hex}.gd"
    path = os.path.join(project_path, name)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    return path


def run_godot(godot_path: str, project_path: str, script_path: str, timeout: int) -> int:
    if not os.path.isfile(godot_path):
        print(f"ERROR: Godot executable not found: {godot_path}", file=sys.stderr)
        return 10

    if not os.path.isdir(project_path):
        print(f"ERROR: Project path not found: {project_path}", file=sys.stderr)
        return 11

    if not os.path.isfile(os.path.join(project_path, "project.godot")):
        print("ERROR: project.godot not found", file=sys.stderr)
        return 12

    cmd = [
        godot_path,
        "--headless",
        "--path", project_path,
        "--script", script_path,
    ]

    creationflags = 0
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=creationflags,
    )

    try:
        start = time.time()

        while True:
            if process.stdout is None:
                break

            line = process.stdout.readline()
            if line:
                line = line.rstrip("\n")

                if line.startswith("Godot Engine v"):
                    pass
                elif line.startswith("[godot_execute]"):
                    pass
                else:
                    print(line)

            if process.poll() is not None:
                rest = process.stdout.read()
                if rest:
                    for extra_line in rest.splitlines():
                        if extra_line.startswith("Godot Engine v"):
                            continue
                        if extra_line.startswith("[godot_execute]"):
                            continue
                        print(extra_line)
                break

            if time.time() - start > timeout:
                print(f"ERROR: Timeout after {timeout} seconds", file=sys.stderr)
                process.kill()
                return 13

        return process.returncode or 0
    finally:
        if process.poll() is None:
            process.kill()


def main():
    gd_path = find_godot()

    parser = argparse.ArgumentParser(
        description="Run inline GDScript body against the project's main scene and print returned result."
    )
    parser.add_argument(
        "script",
        help="Inline GDScript function body OR path to file with function body."
    )
    parser.add_argument(
        "--godot",
        default=gd_path,
        help=f"Path to Godot executable. Default: {gd_path}"
    )
    parser.add_argument(
        "--project",
        default=DEFAULT_PROJECT_PATH,
        help=f"Path to Godot project. Default: {DEFAULT_PROJECT_PATH}"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="Execution timeout in seconds."
    )

    args = parser.parse_args()

    main_scene, main_scene_error = read_main_scene(args.project)
    if not main_scene:
        print(f"ERROR: {main_scene_error}", file=sys.stderr)
        sys.exit(20)

    user_code = resolve_script_arg(args.script)
    wrapper = build_wrapper_script(main_scene, user_code)

    temp_script_path = None
    try:
        temp_script_path = make_temp_script(args.project, wrapper)
        exit_code = run_godot(args.godot, args.project, temp_script_path, args.timeout)
        sys.exit(exit_code)
    finally:
        if temp_script_path and os.path.exists(temp_script_path):
            try:
                os.remove(temp_script_path)
            except OSError:
                pass


if __name__ == "__main__":
    main()