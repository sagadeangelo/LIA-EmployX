from pathlib import Path

# ===============================================================
# LIA EmployX
#
# Crear estructura del Orchestrator
# ===============================================================

ROOT = Path(
    r"D:\PROYECTOS_FLUTTER\lia-employx\backend\orchestrator"
)

ROOT.mkdir(parents=True, exist_ok=True)

FILES = {

"__init__.py": '''"""
LIA EmployX

Orchestrator Package
"""
''',

"orchestrator.py": '''"""
Employ