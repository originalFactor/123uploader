import ast
import sys


def update_all(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    # 提取所有不以下划线开头的顶层类和函数名
    names = [
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))
        and not node.name.startswith("_")
    ]

    all_statement = f"__all__ = {repr(names)}"

    # 检查是否已经存在 __all__，如果存在则替换，否则在开头插入
    lines = source.splitlines()
    found = False
    for i, line in enumerate(lines):
        if line.startswith("__all__ ="):
            lines[i] = all_statement
            found = True
            break

    if not found:
        lines.insert(0, all_statement)
        lines.insert(1, "")  # 加个空行

    with open(file_path, "w", encoding="utf-8") as f:
        _ = f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        update_all(sys.argv[1])
