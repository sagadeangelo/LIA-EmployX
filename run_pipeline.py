import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from backend.modules.cv.loader.loader_factory import LoaderFactory
from backend.modules.cv.parser.cv_section_splitter import CVSectionSplitter
from backend.modules.cv.builders.cv_document_builder import CVDocumentBuilder
from backend.modules.cv.language.language_detector import LanguageDetector
from backend.modules.cv.models.cv_metadata import CVMetadata
from datetime import datetime

def main():
    file_path = "data/uploads/5caccf4a7aa9483db0427c1186818e00_CV_Miguel_Tovar_Full_Stack_English.docx"
    
    loader_factory = LoaderFactory()
    loader = loader_factory.get_loader(Path(file_path))
    extraction_result = loader.extract(file_path)
    raw_text = extraction_result.raw_text
    
    splitter = CVSectionSplitter()
    sections = splitter.split(raw_text)
    
    print("=" * 60)
    print("CV SECTION SPLITTER RESULTS")
    print("=" * 60)
    for name, result in sections.items():
        print(f"{name}: {len(result.text)} chars")
        
    print("\n" + "=" * 60)
    print("BUILDER EXECUTION")
    print("=" * 60)
    
    detector = LanguageDetector()
    language_result = detector.detect(raw_text)
    
    metadata = CVMetadata(
        file_name="CV.docx",
        original_name="CV.docx",
        extension=".docx",
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        file_size=1000,
        uploaded_at=datetime.utcnow(),
        storage_path="mock",
        extractor="DOCXLoader"
    )
    
    try:
        builder = CVDocumentBuilder()
        document = builder.build(
            metadata=metadata,
            raw_text=raw_text,
            sections=sections,
            language=language_result
        )
        print("CVDocument built successfully!")
        
        print("\n--- RESULTS ---")
        print(f"Personal Info Valid: {document.personal_info is not None}")
        if document.personal_info:
            print(f"Name: {document.personal_info.full_name}")
            print(f"Email: {document.personal_info.email}")
            
        print(f"Experience count: {len(document.experience)}")
        print(f"Education count: {len(document.education)}")
        print(f"Skills categories count: {len(document.skills)}")
        for category, skills in document.skills.items():
            print(f"  - {category}: {len(skills)} skills")
            
        print(f"Languages count: {len(document.languages)}")
        print(f"Certifications count: {len(document.certifications)}")
        
    except Exception as e:
        print(f"BUILDER FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        
if __name__ == '__main__':
    main()
