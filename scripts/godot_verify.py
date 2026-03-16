import subprocess
import os
import time
import re
import signal

# путь к Godot
GODOT_PATH = r"/home/imkoi/Documents/Godot_v4.6.1-stable_linux.x86_64"

# путь к проекту
PROJECT_PATH = r"/home/imkoi/gemini-test"

# сколько секунд запускать игру после появления строки Godot Engine v...
GAME_RUN_TIME = 2


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


def open_scene(scene_path):
    cmd = [
        GODOT_PATH,
        "--headless",
        "--path", PROJECT_PATH,
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


def find_main_scene():
    project_file = os.path.join(PROJECT_PATH, "project.godot")

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
            return os.path.join(PROJECT_PATH, scene)

    return None


def kill_process_tree(process):
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    except Exception:
        try:
            process.terminate()
        except Exception:
            pass

    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass


def run_main_scene(scene_path):
    cmd = [
        GODOT_PATH,
        "--path", PROJECT_PATH,
        scene_path
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        preexec_fn=os.setsid
    )

    collected_lines = []
    start_time = None

    try:
        while True:
            if process.stdout is None:
                break

            line = process.stdout.readline()

            if line:
                stripped = line.rstrip("\n")
                collected_lines.append(stripped)

                if start_time is None and stripped.startswith("Godot Engine v"):
                    start_time = time.time()

            if process.poll() is not None:
                rest = process.stdout.read() if process.stdout else ""
                if rest:
                    collected_lines.extend(rest.splitlines())
                break

            if start_time is not None and (time.time() - start_time) >= GAME_RUN_TIME:
                break

        kill_process_tree(process)

        if process.stdout is not None:
            try:
                rest = process.stdout.read()
                if rest:
                    collected_lines.extend(rest.splitlines())
            except Exception:
                pass

    finally:
        if process.poll() is None:
            kill_process_tree(process)

    return extract_warnings_and_errors("\n".join(collected_lines))


def main():
    if not os.path.isfile(GODOT_PATH):
        print(f"ERROR: Godot executable not found: {GODOT_PATH}")
        return

    if not os.path.isdir(PROJECT_PATH):
        print(f"ERROR: Project path not found: {PROJECT_PATH}")
        return

    scenes = find_scenes(PROJECT_PATH)
    total_errors = 0
    total_warnings = 0
    all_logs = []

    print(f"Scanning project with {len(scenes)} scenes...")

    for scene in scenes:
        errors, warnings, logs = open_scene(scene)
        total_errors += errors
        total_warnings += warnings
        all_logs.extend(logs)

    main_scene = find_main_scene()
    if main_scene:
        errors, warnings, logs = run_main_scene(main_scene)
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