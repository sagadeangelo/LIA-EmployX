"""
Primer test del Smart CV Engine.
"""

from backend.modules.cv.engine.pipeline import SmartCVPipeline


pipeline = SmartCVPipeline()

document = pipeline.process(
    r"D:\PROYECTOS_FLUTTER\lia-employx\backend\tests\sample_files\CV_Miguel_Tovar_logistica_Spanish.pdf"
)

print()

print("=" * 80)
print("RESUMEN")
print("=" * 80)

print(document.summary())