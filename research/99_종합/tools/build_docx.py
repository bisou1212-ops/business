import sys, os, re, csv, subprocess, zipfile, shutil
repo, S, out = sys.argv[1], sys.argv[2], sys.argv[3]
import json
toc = json.load(open(sys.argv[4], encoding='utf-8')) if len(sys.argv) > 4 else None
R = lambda p: os.path.join(repo, 'research', p)
PB = '\n\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n\n'
order = [
 ('99_종합/00_2027_TPC_종합보고서.md', None),
 ('00_조사로드맵_및_목차.md', None),
 ('00_TPC_제품기준표.md', None),
 ('01_반도체/01_반도체_심층조사.md', None),
 ('02_디스플레이/02_디스플레이_심층조사.md', None),
 ('03_2차전지/03_2차전지_심층조사.md', None),
 ('04_자동차_전장/04_자동차_전장_심층조사.md', None),
 ('05_일반자동화_산업기계/05_일반자동화_산업기계_심층조사.md', None),
 ('06_로봇_휴머노이드/06_로봇_휴머노이드_심층조사.md', None),
 ('07_광학검사_의료바이오/07_광학검사_의료바이오_심층조사.md', None),
 ('99_종합/05_제품별_적용시장_분석.md', None),
]
def clean(t):
    t = t.replace('✅', '[완료]').replace('⚠️', '[확인 필요]').replace('⚠', '[확인 필요]')
    return t
parts = []
for f, _ in order:
    parts.append(clean(open(R(f), encoding='utf-8').read()))
# appendix: compact unit DB
rows = list(csv.reader(open(R('99_종합/04_통합_장비유닛_DB.csv'), encoding='utf-8-sig')))
H = {h: i for i, h in enumerate(rows[0])}
ind = {'SC':'반도체','DP':'디스플레이','BT':'2차전지','AU':'자동차·전장','GA':'일반자동화','RB':'로봇·휴머노이드','OB':'광학검사·의료바이오'}
ap = ['# 부록. 통합 장비-유닛 데이터베이스 (요약)', '',
      f'- 원본: `research/99_종합/04_통합_장비유닛_DB.csv` ({len(rows)-1}개 유닛, 20개 열). 이 부록은 주요 6개 열만 싣는다.',
      '- 영업기회등급: S 최우선, A 우선, B 보통, C 낮음. 구동방식·요구사양은 원본 CSV 참조. 대부분 [추정] 구조다.', '',
      '| ID | 산업 | 장비명 | 세부유닛 | 예상 TPC 제품군 | 등급 |',
      '|----|----|----------|----------|--------------|--|']
for r in rows[1:]:
    c = lambda k: r[H[k]].replace('|', '/').replace(';', ', ')
    ap.append(f"| {r[0]} | {ind[r[0][:2]]} | {c('장비명')} | {c('세부유닛')} | {c('예상TPC제품군')} | {c('영업기회등급')} |")
parts.append('\n'.join(ap))
md = PB.join(parts)
titles = [re.match(r'#\s+(.*)', p.strip().splitlines()[0]).group(1) for p in parts]
json.dump(titles, open(S + '/titles.json', 'w', encoding='utf-8'), ensure_ascii=False)
open(S + '/all.md', 'w', encoding='utf-8').write(md)
subprocess.run(['pandoc', S + '/all.md', '-f', 'markdown+lists_without_preceding_blankline-yaml_metadata_block', '-o', S + '/raw.docx', '--toc', '--toc-depth=1',
  '-M', 'title=2027 산업·시장·자동화 장비 종합 심층조사', '-M', 'subtitle=TPC로보틱스 기술영업 전략 수립을 위한 선행조사 (7개 산업 + 종합전략)',
  '-M', 'date=조사 기준일 2026-11-24', '-M', 'toc-title=목차'], check=True)
# post-process
d = S + '/x'; shutil.rmtree(d, ignore_errors=True)
zipfile.ZipFile(S + '/raw.docx').extractall(d)
F = '맑은 고딕'
fonts = f'<w:rFonts w:ascii="{F}" w:eastAsia="{F}" w:hAnsi="{F}" w:cs="{F}" />'
st = open(d + '/word/styles.xml', encoding='utf-8').read()
st = re.sub(r'<w:rFonts [^>]*Theme[^>]*/>', fonts, st)
st = re.sub(r'(<w:rPrDefault>.*?)<w:sz w:val="24"\s*/>(.*?)<w:szCs w:val="24"\s*/>', r'\1<w:sz w:val="21"/>\2<w:szCs w:val="21"/>', st, count=1, flags=re.S)
st = re.sub(r'<w:lang [^>]*/>', '<w:lang w:val="ko-KR" w:eastAsia="ko-KR" w:bidi="ar-SA"/>', st)
def restyle(sid, ppr=None, rpr=None):
    global st
    m = re.search(r'(<w:style [^>]*w:styleId="%s"[^>]*>)(.*?)(</w:style>)' % sid, st, re.S)
    body = m.group(2)
    op = re.search(r'<w:pPr>.*?</w:pPr>|<w:pPr\s*/>', body, re.S)
    orr = re.search(r'<w:rPr>.*?</w:rPr>|<w:rPr\s*/>', body, re.S)
    rest = re.sub(r'<w:pPr>.*?</w:pPr>|<w:pPr\s*/>|<w:rPr>.*?</w:rPr>|<w:rPr\s*/>', '', body, flags=re.S)
    ppr = ppr if ppr is not None else (op.group(0) if op else '')
    rpr = rpr if rpr is not None else (orr.group(0) if orr else '')
    st = st[:m.start()] + m.group(1) + rest + ppr + rpr + m.group(3) + st[m.end():]
navy = '1F3864'
restyle('Compact', '<w:pPr><w:spacing w:before="20" w:after="20" w:line="240" w:lineRule="auto"/></w:pPr>', '<w:rPr><w:sz w:val="17"/><w:szCs w:val="17"/></w:rPr>')
restyle('BodyText', '<w:pPr><w:spacing w:before="60" w:after="100" w:line="300" w:lineRule="auto"/></w:pPr>')
restyle('FirstParagraph', '<w:pPr><w:spacing w:before="60" w:after="100" w:line="300" w:lineRule="auto"/></w:pPr>')
restyle('Title', '<w:pPr><w:keepNext/><w:spacing w:before="2400" w:after="360"/><w:jc w:val="center"/></w:pPr>', f'<w:rPr>{fonts}<w:b/><w:color w:val="{navy}"/><w:sz w:val="52"/><w:szCs w:val="52"/></w:rPr>')
restyle('Subtitle', '<w:pPr><w:spacing w:before="120" w:after="240"/><w:jc w:val="center"/></w:pPr>', f'<w:rPr>{fonts}<w:color w:val="404040"/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr>')
restyle('Date', '<w:pPr><w:spacing w:before="120" w:after="120"/><w:jc w:val="center"/></w:pPr>', f'<w:rPr>{fonts}<w:color w:val="595959"/><w:sz w:val="24"/></w:rPr>')
hb = lambda lvl, sz, before, after, border='': f'<w:pPr><w:keepNext/><w:keepLines/>{border}<w:spacing w:before="{before}" w:after="{after}"/><w:outlineLvl w:val="{lvl}"/></w:pPr>'
restyle('Heading1', hb(0, 32, 0, 200, f'<w:pBdr><w:bottom w:val="single" w:sz="12" w:space="4" w:color="{navy}"/></w:pBdr>'), f'<w:rPr>{fonts}<w:b/><w:color w:val="{navy}"/><w:sz w:val="34"/><w:szCs w:val="34"/></w:rPr>')
restyle('Heading2', hb(1, 28, 320, 120), f'<w:rPr>{fonts}<w:b/><w:color w:val="2E5395"/><w:sz w:val="27"/><w:szCs w:val="27"/></w:rPr>')
restyle('Heading3', hb(2, 24, 220, 80), f'<w:rPr>{fonts}<w:b/><w:color w:val="2E5395"/><w:sz w:val="23"/><w:szCs w:val="23"/></w:rPr>')
restyle('Heading4', hb(3, 22, 160, 60), f'<w:rPr>{fonts}<w:b/><w:color w:val="404040"/><w:sz w:val="22"/></w:rPr>')
restyle('TOCHeading', None, f'<w:rPr>{fonts}<w:b/><w:color w:val="{navy}"/><w:sz w:val="32"/></w:rPr>')
# table style: borders + header shading
b = 'w:val="single" w:sz="4" w:space="0" w:color="A6A6A6"'
st = st.replace('<w:tblCellMar>', f'<w:tblBorders><w:top {b}/><w:left {b}/><w:bottom {b}/><w:right {b}/><w:insideH {b}/><w:insideV {b}/></w:tblBorders><w:tblCellMar>', 1)
st = re.sub(r'(<w:tblStylePr w:type="firstRow">.*?)<w:tcPr>.*?</w:tcPr>', r'\1<w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="D9E2F3"/><w:vAlign w:val="center"/></w:tcPr>', st, count=1, flags=re.S)
st = st.replace('<w:tblStylePr w:type="firstRow">', '<w:tblStylePr w:type="firstRow"><w:rPr><w:b/></w:rPr>', 1)
st = st.replace('<w:color w:val="345A8A" />&gt;', '<w:color w:val="345A8A" />')
st = re.sub(r'(<w:jc w:val="center" />)(\s*)(<w:spacing w:after="0" w:before="300" />)', r'\3\2\1', st)
open(d + '/word/styles.xml', 'w', encoding='utf-8').write(st)
doc = open(d + '/word/document.xml', encoding='utf-8').read()
# blockquote -> pandoc uses BlockText style; keep. Landscape A4 section with page numbers footer
sect = ('<w:sectPr><w:footerReference w:type="default" r:id="rIdFooter1"/>'
        '<w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/>'
        '<w:pgMar w:top="1080" w:right="1080" w:bottom="1080" w:left="1080" w:header="567" w:footer="567" w:gutter="0"/>'
        '<w:pgNumType w:start="1"/><w:titlePg/></w:sectPr>')
doc = re.sub(r'<w:sectPr\s*/>|<w:sectPr.*?</w:sectPr>', '', doc, flags=re.S)
doc = doc.replace('</w:body>', sect + '</w:body>')
# table header rows repeat across pages
doc = re.sub(r'(<w:tr>)(\s*<w:trPr>)?', lambda m: m.group(0), doc)
doc = doc.replace('<w:tblHeader w:val="false" />', '')
PBR = '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
doc = doc.replace('<w:sdt>', PBR + '<w:sdt>', 1).replace('</w:sdt>', '</w:sdt>' + PBR, 1)
if toc:
    tab = '<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="14670"/></w:tabs>'
    paras = []
    for i, (t, pg) in enumerate(toc):
        t = t.replace('&', '&amp;').replace('<', '&lt;')
        head = '<w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r><w:r><w:instrText xml:space="preserve">TOC \\o &quot;1-1&quot; \\h \\z \\u</w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r>' if i == 0 else ''
        tail = '</w:r><w:r><w:fldChar w:fldCharType="end"/>' if i == len(toc) - 1 else ''
        paras.append(f'<w:p><w:pPr>{tab}<w:spacing w:before="80" w:after="80"/></w:pPr><w:r>{head}<w:t xml:space="preserve">{t}</w:t><w:tab/><w:t>{pg}</w:t>{tail}</w:r></w:p>')
    doc = re.sub(r'(<w:pStyle w:val="TOCHeading" />.*?</w:p>)<w:p><w:r><w:fldChar w:fldCharType="begin".*?</w:p>', lambda m: m.group(1) + ''.join(paras), doc, count=1, flags=re.S)
open(d + '/word/document.xml', 'w', encoding='utf-8').write(doc)
footer = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
          f'<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr>{fonts}<w:sz w:val="18"/><w:color w:val="7F7F7F"/></w:rPr><w:t xml:space="preserve">2027 산업·시장·자동화 장비 종합 심층조사  |  </w:t></w:r>'
          f'<w:r><w:rPr><w:sz w:val="18"/><w:color w:val="7F7F7F"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:rPr><w:sz w:val="18"/><w:color w:val="7F7F7F"/></w:rPr><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r><w:r><w:rPr><w:sz w:val="18"/></w:rPr><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:rPr><w:sz w:val="18"/><w:color w:val="7F7F7F"/></w:rPr><w:t>1</w:t></w:r><w:r><w:rPr><w:sz w:val="18"/></w:rPr><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>')
open(d + '/word/footer1.xml', 'w', encoding='utf-8').write(footer)
rel = open(d + '/word/_rels/document.xml.rels', encoding='utf-8').read()
rel = rel.replace('</Relationships>', '<Relationship Id="rIdFooter1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/></Relationships>')
open(d + '/word/_rels/document.xml.rels', 'w', encoding='utf-8').write(rel)
ct = open(d + '/[Content_Types].xml', encoding='utf-8').read()
ct = ct.replace('</Types>', '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
open(d + '/[Content_Types].xml', 'w', encoding='utf-8').write(ct)
se = open(d + '/word/settings.xml', encoding='utf-8').read()
if 'updateFields' not in se:
    se = re.sub(r'(<w:settings[^>]*>)', r'\1<w:updateFields w:val="true"/>', se, count=1)
open(d + '/word/settings.xml', 'w', encoding='utf-8').write(se)
if os.path.exists(out): os.remove(out)
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(d):
        for f in files:
            p = os.path.join(root, f); a = os.path.relpath(p, d)
            z.write(p, a)
print('ok', out)
