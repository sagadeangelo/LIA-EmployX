"""
Prueba Automatizada E2E del Pipeline de Extracción de CV
Audita desde el Loader hasta el Repositorio de Perfiles
"""
import os
import traceback
from pathlib import Path

from backend.modules.cv.services.extraction_service import ExtractionService
from backend.modules.cv.mappers.professional_profile_mapper import ProfessionalProfileMapper
from backend.modules.profile.services.profile_service import ProfileService

# Un CV de muestra completo
_SAMPLE_CV = """
Miguel Tovar
miguel@example.com | +52 55 1234 5678
Ciudad de México, México

► Perfil Profesional

Ingeniero de Software con más de 8 años de experiencia en desarrollo
de aplicaciones móviles y backend.

Empresa Alpha — Senior Flutter Developer (2021 – presente)
- Desarrollo de apps multiplataforma con Flutter y Dart.

Empresa Beta — Python Backend Developer (2018 – 2021)
- APIs REST con FastAPI y Django.

Universidad Nacional Autónoma
Licenciatura en Ingeniería en Sistemas Computacionales — 2017

◆ HABILIDADES CLAVE

Flutter · Dart · Python · FastAPI · Docker · AWS · PostgreSQL

IDIOMAS

Español — Nativo
Inglés — C1 (TOEFL 110)

Certificaciones (2023)

AWS Certified Developer – Associate (2023)
Google Cloud Professional Data Engineer (2022)

Proyectos Personales

LIA EmployX — Plataforma de reclutamiento con IA
OpenResume — Generador de CVs de código abierto
"""


def run_e2e_audit():
    print("==================================================")
    print(" INICIANDO AUDITORÍA E2E DE PIPELINE DE EXTRACCIÓN ")
    print("==================================================")

    file_path = "test_sample_cv.docx"
    try:
        import docx
        doc = docx.Document()
        doc.add_paragraph(_SAMPLE_CV)
        doc.save(file_path)
    except ImportError:
        print("[!] python-docx no instalado. Creando txt y saltando LoaderFactory.")
        file_path = "test_sample_cv.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(_SAMPLE_CV)

    try:
        # PASO 1 y 2: ExtractionService (Loader -> Splitter -> Builder)
        print("\n[1] Ejecutando ExtractionService (Loader -> Splitter -> Builder)...")
        service = ExtractionService()
        document = service.process(file_path, mission_id="audit_e2e")
        
        print(f"✅ Documento construido exitosamente.")
        print(f"   -> Nombre extraído: {document.contact.name}")
        
        # Validar Builder:
        print("\n[2] Validando Builder (Experiences y Education)...")
        print(f"   -> document.experiences count: {len(document.experiences)}")
        if not document.experiences:
            print("[FAIL] El ExperienceBuilder devolvió una lista vacía de experiencias.")
            print("   (Se detiene la auditoría aquí para analizar causa raíz en el Builder)")
            
            # Print de diagnóstico del splitter
            print("\n--- DIAGNÓSTICO DEL SPLITTER ---")
            print("Texto que recibió el ExperienceBuilder (sections['experience']):")
            print("---------------------------------------------------------------")
            exp_text = document.sections.get("experience", "")
            print(exp_text if exp_text else "(VACÍO)")
            print("---------------------------------------------------------------")
            
            assert False, "ExperienceBuilder no logró convertir el bloque de texto en objetos CVExperience."
        else:
            print(f"[OK] Builder logró construir {len(document.experiences)} experiencias.")
            for exp in document.experiences:
                print(f"      - {exp.company} | {exp.title}")

        # PASO 3: Mapper
        print("\n[3] Mapeando a ProfessionalProfile (Mapper)...")
        profile = ProfessionalProfileMapper.from_cv_document(document)
        print("[OK] Mapper completado.")
        
        assert profile.experience, "El profile.experience está vacío tras el mapeo."
        print(f"   -> profile.experience count: {len(profile.experience)}")
        
        # PASO 4: Repository (ProfileService)
        print("\n[4] Guardando en Repositorio (ProfileService)...")
        profile_service = ProfileService()
        # Ensure we have a profile ID
        if not profile.id:
            profile.id = "e2e_test_profile"
        
        profile_service.save_profile(profile)
        print("[OK] Perfil guardado exitosamente en JSON.")

        # PASO 5: API Get Simulation
        print("\n[5] Simulando GET /profile...")
        fetched_profile = profile_service.get_profile(profile.id)
        assert fetched_profile is not None, "No se pudo recuperar el perfil."
        
        print(f"[OK] Perfil recuperado: {fetched_profile.personal_info.full_name}")
        print(f"   -> Experiencias recuperadas: {len(fetched_profile.experience)}")
        if len(fetched_profile.experience) == 0:
            print("[FAIL] La experiencia se perdió al guardar o recuperar del JSON.")
            assert False, "Pérdida de datos en persistencia."
        
        print("\n==================================================")
        print(" LA AUDITORÍA E2E PASÓ CON ÉXITO ")
        print("==================================================")
        
    except AssertionError as e:
        print(f"\n[WARNING] AUDITORÍA DETENIDA: {e}")
    except Exception as e:
        print(f"\n[ERROR] ERROR INESPERADO: {e}")
        traceback.print_exc()
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    run_e2e_audit()
