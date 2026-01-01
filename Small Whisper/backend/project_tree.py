import os

# ================================
# CONFIG
# ================================
EXCLUDED_DIRS = {
    "venv",
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "node_modules"
}

EXCLUDED_FILES_EXT = {
    ".pyc",
    ".pyo",
    ".log"
}

MAX_DEPTH = 10  # غيّرها إذا بدك عمق أكبر

# ================================
# TREE FUNCTION
# ================================
def print_tree(root_path, prefix="", depth=0):
    if depth > MAX_DEPTH:
        return

    try:
        items = sorted(os.listdir(root_path))
    except PermissionError:
        return

    for index, item in enumerate(items):
        path = os.path.join(root_path, item)

        if item in EXCLUDED_DIRS:
            continue

        if os.path.isfile(path):
            if any(item.endswith(ext) for ext in EXCLUDED_FILES_EXT):
                continue

        connector = "└── " if index == len(items) - 1 else "├── "
        print(prefix + connector + item)

        if os.path.isdir(path):
            extension = "    " if index == len(items) - 1 else "│   "
            print_tree(path, prefix + extension, depth + 1)

# ================================
# RUN
# ================================
if __name__ == "__main__":
    root_dir = os.getcwd()
    print(f"\n📂 Project Structure: {root_dir}\n")
    print_tree(root_dir)
