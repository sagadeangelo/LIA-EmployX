import sys
from pathlib import Path
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.modules.cv.loader.docx_loader import DOCXLoader
from backend.modules.cv.loader.extraction_strategy_resolver import ExtractionChunkMerger
from backend.modules.cv.parser.cv_section_splitter import CVSectionSplitter
from backend.modules.cv.builders.cv_document_builder import CVDocumentBuilder

def run_pipeline():
    docx_path = r"D:\PROYECTOS_FLUTTER\lia-employx\data\uploads\5caccf4a7aa9483db0427c1186818e00_CV_Miguel_Tovar_Full_Stack_English.docx"
    
    # 1. Load (already merges inside)
    loader = DOCXLoader()
    merged_text = loader.load(docx_path)
    
    # 2. Split
    splitter = CVSectionSplitter()
    section_map = splitter.split(merged_text)
    
    # 4. Build Document
    builder = CVDocumentBuilder()
    
    from backend.modules.cv.models.cv_metadata import CVMetadata
    from backend.modules.cv.language.language_result import LanguageResult
    
    from datetime import datetime
    metadata = CVMetadata(
        file_name="CV_Miguel_Tovar_Full_Stack_English.docx",
        original_name="CV_Miguel.docx",
        extension=".docx",
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        uploaded_at=datetime.now(),
        storage_path="/path/to/file",
        file_size=1024
    )
    language = LanguageResult(language="en", language_name="English", confidence=1.0)
    
    doc = builder.build(metadata=metadata, raw_text=merged_text, sections=section_map, language=language)
    
    # Validation output
    print("================== CVDocument Summary ==================")
    print(f"PersonalInfo: {'populated' if doc.contact else 'missing'}")
    print(f"Experiences: {len(doc.experiences)}")
    print(f"Education: {len(doc.education)}")
    print(f"Skills: {len(doc.skills)}")
    print(f"Languages: {len(doc.languages)}")
    print(f"Certifications: {len(doc.certifications)}")
    
    import sys
    # Add a safe print helper
    def safe_print(text):
        print(text.encode('cp1252', errors='replace').decode('cp1252'))

    safe_print("\n--- Experiences Data ---")
    for exp in doc.experiences[:3]:
        safe_print(f"Company: {exp.company} | Pos: {exp.position} | Start: {exp.start_date} | End: {exp.end_date}")
        
    safe_print("\n--- Education Data ---")
    for edu in doc.education[:3]:
        safe_print(f"Inst: {edu.institution} | Degree: {edu.degree}")
        
    safe_print("\n--- Skills Data ---")
    for skill in doc.skills[:5]:
        safe_print(f"Name: {skill.name} | Category: {skill.category}")
            
    safe_print("\n--- Languages Data ---")
    for lang in doc.languages:
        safe_print(f"Name: {lang.name} | Level: {lang.level}")
        
    safe_print("\n--- Certifications Data ---")
    for cert in doc.certifications:
        safe_print(f"Name: {cert}")

if __name__ == '__main__':
    run_pipeline()
