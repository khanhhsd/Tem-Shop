from pathlib import Path
import zipfile
from xml.etree import ElementTree as ET

p = Path(r'd:\hocj\He_Thong_Thong_tin\E-Commerce demo\inf_sys_analysis_design_assignment_06_design_code.docx')
out = Path(r'd:\hocj\He_Thong_Thong_tin\E-Commerce demo\assignment_text.txt')

with zipfile.ZipFile(p) as z:
    xml = z.read('word/document.xml')

root = ET.fromstring(xml)
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
paras = []
for pnode in root.findall('.//w:p', ns):
    txt = ''.join(t.text or '' for t in pnode.findall('.//w:t', ns))
    paras.append(txt)

out.write_text('\n'.join(paras), encoding='utf-8')
print(f'Wrote {out} with {len(paras)} paragraphs')
