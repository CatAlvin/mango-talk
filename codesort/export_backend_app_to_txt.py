from pathlib import Path


PROJECT_ROOT = Path("/home/projects/mango-talk").resolve()
SOURCE_ROOT = (PROJECT_ROOT / "backend" / "app").resolve()
OUTPUT_ROOT = (PROJECT_ROOT / "codesort" / "code").resolve()


def build_output_name(py_file: Path) -> str:
    """
    把 /home/projects/mango-talk/backend/app/models/user.py
    变成 backend.app.models.user.txt
    """
    relative_to_project = py_file.relative_to(PROJECT_ROOT)
    relative_without_suffix = relative_to_project.with_suffix("")
    return ".".join(relative_without_suffix.parts) + ".txt"


def build_header_path(py_file: Path) -> str:
    """
    生成写入 txt 文件开头的路径：
    mango-talk/backend/app/models/user.py
    """
    relative_to_project = py_file.relative_to(PROJECT_ROOT)
    return f"{PROJECT_ROOT.name}/{relative_to_project.as_posix()}"


def export_py_files_to_txt() -> None:
    if not SOURCE_ROOT.exists():
        raise FileNotFoundError(f"源目录不存在: {SOURCE_ROOT}")

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    py_files = sorted(SOURCE_ROOT.rglob("*.py"))

    if not py_files:
        print(f"未找到任何 .py 文件: {SOURCE_ROOT}")
        return

    count = 0

    for py_file in py_files:
        output_name = build_output_name(py_file)
        output_file = OUTPUT_ROOT / output_name
        header_path = build_header_path(py_file)

        code_text = py_file.read_text(encoding="utf-8")

        output_content = f"{header_path}\n\n{code_text}"

        output_file.write_text(output_content, encoding="utf-8")
        count += 1
        print(f"[OK] {py_file} -> {output_file}")

    print(f"\n完成，共导出 {count} 个文件到: {OUTPUT_ROOT}")


if __name__ == "__main__":
    export_py_files_to_txt()
