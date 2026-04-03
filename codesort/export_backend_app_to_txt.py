from pathlib import Path


PROJECT_ROOT = Path("/home/projects/mango-talk").resolve()
SOURCE_ROOT = (PROJECT_ROOT / "backend" / "app").resolve()
OUTPUT_ROOT = (PROJECT_ROOT / "codesort" / "code").resolve()
OUTPUT_FILE = OUTPUT_ROOT / "mango-talk.backend.txt"


def build_project_relative_path(py_file: Path) -> str:
    """
    生成项目相对路径，例如：
    mango-talk/backend/app/models/user.py
    """
    relative_to_project = py_file.relative_to(PROJECT_ROOT)
    return f"{PROJECT_ROOT.name}/{relative_to_project.as_posix()}"


def export_all_py_to_one_txt() -> None:
    if not SOURCE_ROOT.exists():
        raise FileNotFoundError(f"源目录不存在: {SOURCE_ROOT}")

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    py_files = sorted(SOURCE_ROOT.rglob("*.py"))

    if not py_files:
        print(f"未找到任何 .py 文件: {SOURCE_ROOT}")
        return

    parts = []

    for py_file in py_files:
        project_path = build_project_relative_path(py_file)
        absolute_path = str(py_file.resolve())
        code_text = py_file.read_text(encoding="utf-8", errors="replace")

        block = (
            "=" * 100 + "\n"
            f"PATH: {project_path}\n"
            f"ABSOLUTE_PATH: {absolute_path}\n"
            + "=" * 100 + "\n\n"
            + code_text
            + "\n\n"
        )
        parts.append(block)

    final_text = "".join(parts)
    OUTPUT_FILE.write_text(final_text, encoding="utf-8")

    print(f"完成，共整理 {len(py_files)} 个 .py 文件")
    print(f"输出文件: {OUTPUT_FILE}")


if __name__ == "__main__":
    export_all_py_to_one_txt()
