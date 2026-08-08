import sys
from pathlib import Path
sys.path.append(str(Path('.').absolute()))
from zipfile import ZipFile
from lxml import etree

path = r'D:\PROYECTOS_FLUTTER\lia-employx\data\uploads\5caccf4a7aa9483db0427c1186818e00_CV_Miguel_Tovar_Full_Stack_English.docx'
with ZipFile(path) as z:
    doc_xml = z.read('word/document.xml')

root = etree.fromstring(doc_xml)

NS_FULL = {
    'w':   'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a':   'http://schemas.openxmlformats.org/drawingml/2006/main',
    'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape',
    'mc':  'http://schemas.openxmlformats.org/markup-compatibility/2006',
}

lines = []

# Check all mc:AlternateContent fallback text
alt = root.xpath('.//mc:AlternateContent', namespaces=NS_FULL)
lines.append(f'mc:AlternateContent count: {len(alt)}')
for i, a in enumerate(alt):
    fallback = a.xpath('mc:Fallback', namespaces=NS_FULL)
    for f in fallback:
        texts = f.xpath('.//w:t', namespaces=NS_FULL)
        txt = ''.join(t.text or '' for t in texts).strip()
        if txt:
            lines.append(f'[AlternateContent {i} fallback]: {txt[:200]}')

# First wps:txbx full XML
wps_ns = 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape'
txbx_elems = root.findall(f'.//{{{wps_ns}}}txbx')
lines.append(f'\nFirst wps:txbx XML:')
if txbx_elems:
    lines.append(etree.tostring(txbx_elems[0], encoding='unicode')[:1200])

Path('alt_content_report.txt').write_text('\n'.join(lines), encoding='utf-8')
print('Written to alt_content_report.txt')
