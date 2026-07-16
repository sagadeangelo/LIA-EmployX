from pathlib import Path

# ============================================================
# LIA EmployX - Crear módulos del Backend
# ============================================================

ROOT = Path(r"D:\PROYECTOS_FLUTTER\lia-employx\backend\modules")

MODULES = [
    "auth",
    "users",
    "cv",
    "jobs",
    "learning",
    "books",
    "certifications",
    "notifications",
]

SUBFOLDERS = [
    "controllers",
    "services",
    "repositories",
    "models",
    "schemas",
    "utils",
]

FILES = [
    "__init__.py",
    "router.py",
    "service.py",
    "repository.py",
    "models.py",
    "schemas.py",
    "constants.py",
]

print("\n========================================")
print("Creando módulos de LIA EmployX...")
print("========================================\n")

ROOT.mkdir(parents=True, exist_ok=True)

for module in MODULES:

    module_path = ROOT / module
    module_path.mkdir(parents=True, exist_ok=True)

    # Crear subcarpetas
    for folder in SUBFOLDERS:

        folder_path = module_path / folder
        folder_path.mkdir(exist_ok=True)

        init_file = folder_path / "__init__.py"

        if not init_file.exists():
            init_file.write_text(
                f'"""Paquete {folder} del módulo {module}."""\n',
                encoding="utf-8"
            )

    # Crear archivos principales
    for file in FILES:

        file_path = module_path / file

        if not file_path.exists():

            if file == "__init__.py":
                content = f'"""Módulo {module}."""\n'

            else:
                content = (
                    f'"""{file} del módulo {module}."""\n\n'
                )

            file_path.write_text(content, encoding="utf-8")

    print(f"✓ {module}")

print("\n========================================")
print("Todos los módulos fueron creados.")
print("========================================")