import ast


FORBIDDEN_FUNCTIONS = {
    "open",
    "eval",
    "exec",
    "compile",
    "__import__",
    "input",
}

FORBIDDEN_MODULES = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "requests",
    "pathlib",
    "shutil",
    "pickle",
    "importlib",
}


def validate_code(code: str) -> None:


    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise ValueError(f"Syntax error: {e}")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split(".")[0]
                if module_name in FORBIDDEN_MODULES:
                    raise ValueError(f"Запрещён импорт модуля: {module_name}")

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_name = node.module.split(".")[0]
                if module_name in FORBIDDEN_MODULES:
                    raise ValueError(f"Запрещён импорт модуля: {module_name}")

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in FORBIDDEN_FUNCTIONS:
                    raise ValueError(f"Запрещён вызов функции: {func_name}")

        elif isinstance(node, ast.Attribute):
            if node.attr.startswith("__"):
                raise ValueError("Доступ к dunder-атрибутам запрещён")