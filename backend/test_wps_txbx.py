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
    'w':   'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a':   'http://schemas.openxmlformats.org/drawingml/2006/main',
    'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape',
    'wp':  'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'mc':  'http://schemas.openxmlformats.org/markup-compatibility/2006',
}

lines = []
txbx_elements = root.xpath('.//wps:txbx', namespaces=NS)
lines.append(f'wps:txbx count: {len(txbx_elements)}')
for i, txbx in enumerate(txbx_elements):
    lines.append(f'\n--- wps:txbx [{i}] ---')
    # Get all text nodes (both w:t and a:t)
    w_texts = txbx.xpath('.//w:t', namespaces=NS)
    a_texts = txbx.xpath('.//a:t', namespaces=NS)
    combined = []
    for t in w_texts:
        if t.text: combined.append(t.text)
    for t in a_texts:
        if t.text: combined.append(t.text)
    full = ''.join(combined).strip()
    lines.append(full[:300] if full else '(empty)')

Path('wps_txbx_content.txt').write_text('\n'.join(lines), encoding='utf-8')
print('Written to wps_txbx_content.txt')
