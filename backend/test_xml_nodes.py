import sys
from pathlib import Path
sys.path.append(str(Path('.').absolute()))
from zipfile import ZipFile
from lxml import etree

path = r'D:\PROYECTOS_FLUTTER\lia-employx\data\uploads\5caccf4a7aa9483db0427c1186818e00_CV_Miguel_Tovar_Full_Stack_English.docx'
with ZipFile(path) as z:
    doc_xml = z.read('word/document.xml')

root = etree.fromstring(doc_xml)
NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape',
}

# Write all text nodes to file
lines = []
all_text = root.xpath('.//w:t', namespaces=NS)
lines.append(f'Total w:t nodes: {len(all_text)}')
for i, t in enumerate(all_text):
    if t.text and t.text.strip():
        lines.append(f'[{i}] {t.text.strip()[:100]}')

Path('xml_text_nodes.txt').write_text('\n'.join(lines), encoding='utf-8')
print(f'Written {len(lines)} lines to xml_text_nodes.txt')

# Also check for wps:txbx (WordProcessingShape textboxes, which contain personal info in modern CVs)
txbx = root.xpath('.//wps:txbx', namespaces=NS)
print(f'wps:txbx elements: {len(txbx)}')

# And a:txBody (DrawingML)
a_txt = root.xpath('.//a:t', namespaces=NS)
lines2 = [f'Total a:t nodes: {len(a_txt)}']
for i, t in enumerate(a_txt):
    if t.text and t.text.strip():
        lines2.append(f'[{i}] {t.text.strip()[:100]}')
Path('xml_drawingml_nodes.txt').write_text('\n'.join(lines2), encoding='utf-8')
print(f'Written {len(lines2)} drawingml lines')
