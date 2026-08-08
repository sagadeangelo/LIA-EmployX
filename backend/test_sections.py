import sys
from pathlib import Path
sys.path.append(str(Path('.').absolute()))
from backend.modules.cv.loader.docx_loader import DOCXLoader
from backend.modules.cv.parser.cv_section_splitter import CVSectionSplitter

text = DOCXLoader().load(r'D:\PROYECTOS_FLUTTER\lia-employx\data\uploads\5caccf4a7aa9483db0427c1186818e00_CV_Miguel_Tovar_Full_Stack_English.docx')

# Write full raw text for inspection
Path('raw_text_full.txt').write_text(text, encoding='utf-8', errors='replace')
print('full raw text written. Length:', len(text))

sections = CVSectionSplitter().split(text)
print()
for k, v in sections.items():
    t = v.text if hasattr(v, 'text') else str(v)
    print(f'=== {k} (conf={getattr(v,"confidence","-")}) ===')
    print(t[:200].replace('\n', '↵'))
    print()
