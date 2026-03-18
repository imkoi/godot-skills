import argparse
import os
import re
import shutil
import subprocess


GAME_RUN_TIME = 1


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


def find_gd_files(project_path):
    gd_files = []
    for root, dirs, files in os.walk(project_path):
        for f in files:
            if f.endswith(".gd"):
                gd_files.append(os.path.join(root, f))
    return gd_files


def check_file_length(gd_files, max_lines=300):
    violations = []
    for path in gd_files:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        if len(lines) > max_lines:
            violations.append((path, len(lines)))
    return violations


def check_method_length(gd_files, max_lines=50):
    violations = []
    func_re = re.compile(r'^func\s+(\w+)')
    for path in gd_files:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        current_func = None
        func_start = 0
        for i, line in enumerate(lines):
            m = func_re.match(line)
            if m:
                if current_func is not None:
                    length = i - func_start
                    if length > max_lines:
                        violations.append((path, current_func, length))
                current_func = m.group(1)
                func_start = i
        if current_func is not None:
            length = len(lines) - func_start
            if length > max_lines:
                violations.append((path, current_func, length))
    return violations


def find_scenes(project_path):
    scenes = []
    for root, dirs, files in os.walk(project_path):
        for f in files:
            if f.endswith(".tscn"):
                scenes.append(os.path.join(root, f))
    return scenes


def extract_warnings_and_errors(output: str):
    lines = []
    errors = 0
    warnings = 0

    for line in output.splitlines():
        upper = line.upper()
        if "ERROR" in upper:
            errors += 1
            lines.append(line.strip())
        elif "WARNING" in upper:
            warnings += 1
            lines.append(line.strip())

    return errors, warnings, lines


def open_scene(scene_path, godot_path, project_path):
    cmd = [
        godot_path,
        "--headless",
        "--path", project_path,
        "--quit",
        scene_path
    ]

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    return extract_warnings_and_errors(process.stdout)


def find_main_scene(project_path):
    project_file = os.path.join(project_path, "project.godot")

    if not os.path.exists(project_file):
        return None

    with open(project_file, "r", encoding="utf-8") as f:
        text = f.read()

    patterns = [
        r'application/run/main_scene\s*=\s*"(.+?)"',
        r'run/main_scene\s*=\s*"(.+?)"',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            scene = match.group(1).replace("res://", "")
            return os.path.join(project_path, scene)

    return None



def run_main_scene(scene_path, godot_path, project_path):
    cmd = [
        godot_path,
        "--headless",
        "--quit-after", str(GAME_RUN_TIME),
        "--path", project_path,
        scene_path
    ]

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=GAME_RUN_TIME + 10
    )

    return extract_warnings_and_errors(process.stdout)


def main():
    gd_path = find_godot()

    parser = argparse.ArgumentParser(
        description="Verify a Godot project by opening every scene and running the main scene."
    )
    parser.add_argument(
        "project",
        help="Path to the Godot project directory."
    )
    parser.add_argument(
        "--godot",
        default=gd_path,
        help=f"Path to Godot executable. Default: {gd_path}"
    )
    args = parser.parse_args()

    project_path = args.project
    gd_script = args.godot

    if not os.path.isfile(gd_script):
        print(f"ERROR: Godot executable not found: {gd_script}")
        return

    if not os.path.isdir(project_path):
        print(f"ERROR: Project path not found: {project_path}")
        return

    # Hard gates: .gd file length and method length
    gd_files = find_gd_files(project_path)
    hard_gate_failed = False

    file_violations = check_file_length(gd_files, max_lines=300)
    if file_violations:
        hard_gate_failed = True
        print("HARD GATE FAILED: .gd files exceeding 300 lines:")
        for path, count in file_violations:
            rel = os.path.relpath(path, project_path)
            print(f"  {rel}: {count} lines")

    method_violations = check_method_length(gd_files, max_lines=50)
    if method_violations:
        hard_gate_failed = True
        print("HARD GATE FAILED: methods exceeding 50 lines:")
        for path, func_name, count in method_violations:
            rel = os.path.relpath(path, project_path)
            print(f"  {rel}::{func_name}: {count} lines")

    if hard_gate_failed:
        print("ERROR: Hard gate checks failed. Fix the issues above before proceeding.")
        return

    scenes = find_scenes(project_path)
    total_errors = 0
    total_warnings = 0
    all_logs = []

    print(f"Scanning project with {len(scenes)} scenes...")

    for scene in scenes:
        errors, warnings, logs = open_scene(scene, gd_script, project_path)
        total_errors += errors
        total_warnings += warnings
        all_logs.extend(logs)

    main_scene = find_main_scene(project_path)
    if main_scene:
        errors, warnings, logs = run_main_scene(main_scene, gd_script, project_path)
        total_errors += errors
        total_warnings += warnings
        all_logs.extend(logs)
    else:
        all_logs.append("WARNING: Main scene not found in project.godot")
        total_warnings += 1

    print(f"Verification finished with {total_errors} errors, {total_warnings} warnings")

    for line in all_logs:
        print(line)


if __name__ == "__main__":
    main()