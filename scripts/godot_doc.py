import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


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


def run_doctool(godot_path: str, output_dir: str) -> int:
    if not os.path.isfile(godot_path):
        print(f"ERROR: Godot executable not found: {godot_path}", file=sys.stderr)
        return 1

    cmd = [
        godot_path,
        "--headless",
        "--doctool",
        output_dir,
    ]

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if process.returncode != 0:
        output = process.stdout.strip()
        if output:
            print(output, file=sys.stderr)
        return process.returncode

    return 0


def normalize_text(text):
    if not text:
        return ""
    return " ".join(text.split()).strip()


def resolve_docs_dir(base_dir: str) -> str:
    candidates = [
        os.path.join(base_dir, "doc", "classes"),
        os.path.join(base_dir, "classes"),
        base_dir,
    ]

    for path in candidates:
        if os.path.isdir(path):
            return path

    return base_dir


def find_class_xml(doc_dir: str, class_name: str):
    exact = os.path.join(doc_dir, f"{class_name}.xml")
    if os.path.isfile(exact):
        return exact

    lower_name = class_name.lower()
    for filename in os.listdir(doc_dir):
        if filename.lower() == f"{lower_name}.xml":
            return os.path.join(doc_dir, filename)

    return None


def get_member_description(node: ET.Element) -> str:
    desc = node.find("description")
    if desc is not None:
        return normalize_text("".join(desc.itertext()))
    return ""


def print_class_doc(xml_path: str) -> int:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    class_name = root.attrib.get("name", "Unknown")
    inherits = root.attrib.get("inherits", "")
    brief = normalize_text(root.findtext("brief_description"))
    description = normalize_text(root.findtext("description"))

    print(f"Class: {class_name}")
    if inherits:
        print(f"Inherits: {inherits}")

    if brief:
        print("\nBrief:")
        print(brief)

    if description:
        print("\nDescription:")
        print(description)

    members = root.find("members")
    if members is not None and list(members):
        print("\nProperties:")
        for member in members.findall("member"):
            m_type = member.attrib.get("type", "Variant")
            m_name = member.attrib.get("name", "unknown")
            default = member.attrib.get("default")
            line = f"  - {m_type} {m_name}"
            if default is not None:
                line += f" = {default}"
            print(line)

    methods = root.find("methods")
    if methods is not None and list(methods):
        print("\nMethods:")
        for method in methods.findall("method"):
            m_name = method.attrib.get("name", "unknown")
            return_type = "void"
            ret = method.find("return")
            if ret is not None:
                return_type = ret.attrib.get("type", "Variant")

            params = []
            for arg in method.findall("param"):
                arg_type = arg.attrib.get("type", "Variant")
                arg_name = arg.attrib.get("name", "arg")
                default = arg.attrib.get("default")
                part = f"{arg_type} {arg_name}"
                if default is not None:
                    part += f" = {default}"
                params.append(part)

            print(f"  - {return_type} {m_name}({', '.join(params)})")

    signals = root.find("signals")
    if signals is not None and list(signals):
        print("\nSignals:")
        for signal in signals.findall("signal"):
            s_name = signal.attrib.get("name", "unknown")
            params = []
            for arg in signal.findall("param"):
                arg_type = arg.attrib.get("type", "Variant")
                arg_name = arg.attrib.get("name", "arg")
                params.append(f"{arg_type} {arg_name}")
            print(f"  - {s_name}({', '.join(params)})")

    constants = root.find("constants")
    if constants is not None and list(constants):
        print("\nConstants:")
        for constant in constants.findall("constant"):
            c_name = constant.attrib.get("name", "unknown")
            c_value = constant.attrib.get("value", "")
            line = f"  - {c_name}"
            if c_value:
                line += f" = {c_value}"
            print(line)

    return 0


def main():
    gd_path = find_godot()

    parser = argparse.ArgumentParser(
        description="Get Godot built-in class documentation for a specific type."
    )
    parser.add_argument("class_name", help='Class name, for example: "Node2D"')
    parser.add_argument(
        "--godot",
        default=gd_path,
        help=f"Path to Godot executable. Default: {gd_path}"
    )
    args = parser.parse_args()

    temp_dir = tempfile.mkdtemp(prefix="godot_doctool_")

    try:
        exit_code = run_doctool(args.godot, temp_dir)
        if exit_code != 0:
            sys.exit(exit_code)

        docs_dir = resolve_docs_dir(temp_dir)
        xml_path = find_class_xml(docs_dir, args.class_name)

        if not xml_path:
            print(f'ERROR: Class "{args.class_name}" not found in generated Godot docs.', file=sys.stderr)
            sys.exit(2)

        sys.exit(print_class_doc(xml_path))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()