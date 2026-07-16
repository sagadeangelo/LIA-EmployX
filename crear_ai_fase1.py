from pathlib import Path

ROOT = Path(r"D:\PROYECTOS_FLUTTER\lia-employx\backend\ai")

print("=" * 60)
print("Creando AI Core de LIA EmployX...")
print("=" * 60)

folders = [
    ROOT,
    ROOT / "providers",
    ROOT / "prompts",
    ROOT / "prompts" / "cv",
    ROOT / "prompts" / "ats",
    ROOT / "prompts" / "interview",
    ROOT / "prompts" / "learning",
    ROOT / "prompts" / "translation",
    ROOT / "embeddings",
    ROOT / "memory",
]

for folder in folders:
    folder.mkdir(parents=True, exist_ok=True)
    print(f"✓ {folder}")

files = [

    ROOT / "__init__.py",

    ROOT / "llm_manager.py",

    ROOT / "config.py",

    ROOT / "models_catalog.py",

    ROOT / "providers" / "__init__.py",

    ROOT / "providers" / "base_provider.py",

    ROOT / "providers" / "lmstudio_provider.py",

    ROOT / "prompts" / "__init__.py",

    ROOT / "prompts" / "cv" / "__init__.py",

    ROOT / "prompts" / "ats" / "__init__.py",

    ROOT / "prompts" / "interview" / "__init__.py",

    ROOT / "prompts" / "learning" / "__init__.py",

    ROOT / "prompts" / "translation" / "__init__.py",

    ROOT / "embeddings" / "__init__.py",

    ROOT / "memory" / "__init__.py",

]

for file in files:

    file.touch(exist_ok=True)

    print(f"✓ {file.name}")

print()
print("=" * 60)
print("AI Core creado correctamente.")
print("=" * 60)