
import inspect
import os

import warehouse


def generate_documentation():
    os.makedirs("docs", exist_ok=True)

    lines = [
        "# Warehouse Management System",
        "",
        "## Project description",
        "",
        "A Python application for warehouse management.",
        "",
        "## Class documentation",
        "",
    ]

    for name, obj in inspect.getmembers(warehouse, inspect.isclass):
        if obj.__module__ == warehouse.__name__:
            lines.append(f"### Class `{name}`")
            lines.append("")
            lines.append(inspect.getdoc(obj) or "No description.")
            lines.append("")

            for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                if not method_name.startswith("_"):
                    lines.append(f"#### `{method_name}`")
                    lines.append("")
                    lines.append(inspect.getdoc(method) or "No description.")
                    lines.append("")

    with open("docs/API.md", "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    print("Documentation generated: docs/API.md")


if __name__ == "__main__":
    generate_documentation()
