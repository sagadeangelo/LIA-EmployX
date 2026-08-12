import sys
from pathlib import Path
sys.path.append(str(Path('.').absolute()))
from zipfile import ZipFile
from lxml import etree

path = r'D:\PROYECTOS_FLUTTER\lia-employx\data\uploads\5caccf4a7aa9483db0427c1186818e00_CV_Miguel_Tovar_Full_Stack_English.docx'
with ZipFile(path) as z:
    doc_xml = z.read('word/document.xml')
    # List media files
    media = [n for n in z.namelist() if 'media' in n]
    print('Media files:', media)

root = etree.fromstring(doc_xml)

# All namespaces in this doc
nsmap = {}
for elem in root.iter():
    for prefix, uri in elem.nsmap.items():
        if prefix:
            nsmap[prefix] = uri

NS_FULL = {
    'w':   'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a':   'http://schemas.openxmlformats.org/drawingml/2006/main',
    'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape',
    'mc':  'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'r':   'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'wp':  'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
}

# Check mc:AlternateContent
alt = root.xpath('.//mc:AlternateContent', namespaces=NS_FULL)
print(f'\nmc:AlternateContent count: {len(alt)}')
for i, a in enumerate(alt[:3]):
    fallback = a.xpath('mc:Fallback', namespaces=NS_FULL)
    choice = a.xpath('mc:Choice', namespaces=NS_FULL)
    print(f'  [{i}] choices={len(choice)}, fallbacks={len(fallback)}')
    for f in fallback:
        texts = f.xpath('.//w:t', namespaces=NS_FULL)
        txt = ''.join(t.text or '' for t in texts).strip()
        if txt:
            print(f'    fallback text: {txt[:100]}')

# Check first wps:txbx [0] - the empty one - in full
wps_ns = 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape'
txbx_elems = root.findall(f'.//{{{wps_ns}}}txbx')
print(f'\nFirst txbx raw XML (first 800 chars):')
if txbx_elems:
    print(etree.tostring(txbx_elems[0], encoding='unicode')[:800])
