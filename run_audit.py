import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from backend.modules.cv.loader.loader_factory import LoaderFactory
from backend.modules.cv.parser.cv_section_splitter import CVSectionSplitter

def find_file(filename_substring):
    for root, dirs, files in os.walk('.'):
        if '.venv' in root or '.git' in root:
            continue
        for file in files:
            if filename_substring in file:
                return os.path.join(root, file)
    return None

def main():
    filename_substring = "CV_Miguel_Tovar_Full_Stack_English.docx"
    file_path = find_file(filename_substring)
    if not file_path:
        print(f"File containing {filename_substring} not found.")
        return

    loader_factory = LoaderFactory()
    loader = loader_factory.get_loader(Path(file_path))
    extraction_result = loader.extract(file_path)
    raw_text = extraction_result.raw_text
    
    print("=== RAW TEXT ===")
    print(raw_text)

if __name__ == '__main__':
    main()
