import csv, glob, sys, os, collections
root = sys.argv[1]
files = sorted(glob.glob(os.path.join(root, 'research', '0[1-7]_*', '*_장비유닛_DB.csv')))
rows, header = [], None
for f in files:
    r = list(csv.reader(open(f, encoding='utf-8')))
    header = header or r[0]
    assert r[0] == header, f
    rows += r[1:]
out = os.path.join(root, 'research', '99_종합')
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, '04_통합_장비유닛_DB.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh); w.writerow(header); w.writerows(rows)
H = {h: i for i, h in enumerate(header)}
ind_name = {'SC':'반도체','DP':'디스플레이','BT':'2차전지','AU':'자동차·전장','GA':'일반자동화','RB':'로봇·휴머노이드','OB':'광학검사·의료바이오'}
inds = list(ind_name.values())
products = [('리니어모터',['리니어모터']),('리니어 스테이지',['리니어 스테이지','클린 리니어']),('직교로봇',['직교로봇']),
 ('전동 액추에이터',['전동 액추에이터']),('공압 실린더',['실린더']),('솔레노이드밸브',['솔레노이드밸브','밸브 매니폴드']),
 ('진공기기',['진공']),('그리퍼',['그리퍼']),('에어유닛·압력스위치',['에어유닛','압력스위치']),('크로스롤러',['크로스롤러']),
 ('휴머노이드 액추에이터',['휴머노이드 액추에이터','핑거 관절모듈'])]
cnt = {p: collections.Counter() for p,_ in products}
top = {p: collections.Counter() for p,_ in products}
sunits = {p: [] for p,_ in products}
for r in rows:
    ind = ind_name[r[0][:2]]; tp = r[H['예상TPC제품군']]; g = r[H['영업기회등급']]
    for p, kws in products:
        if any(k in tp for k in kws):
            cnt[p][ind] += 1
            if g in ('S','A'): top[p][ind] += 1
            if g == 'S': sunits[p].append(f"{ind} · {r[H['장비명']]} · {r[H['세부유닛']]}")
L = []
L.append('# 공압 및 모션 제품별 적용시장 분석 (최종 결과물 5)\n')
L.append('- 조사 기준일: 2026-11-24')
L.append(f'- 근거: 7개 산업 장비-유닛 DB 통합본 `04_통합_장비유닛_DB.csv` (총 {len(rows)}개 유닛)에서 "예상TPC제품군" 열을 제품별로 집계했다.')
L.append('- 표기: 숫자는 해당 제품이 적용 가능한 유닛 수, 괄호 안은 그중 영업기회 S·A 등급 유닛 수. 모두 **[가능]** 기준이며 실제 적용 실적과 다르다.')
L.append('- 이 파일은 `research/99_종합/tools/merge_db.py`로 생성했다. 산업별 DB를 고치면 `python3 research/99_종합/tools/merge_db.py .` 로 다시 생성한다.\n')
L.append('## 1. 제품 × 산업 적용 유닛 수\n')
L.append('| 제품 | ' + ' | '.join(inds) + ' | 합계 |')
L.append('|---|' + '---|'*(len(inds)+1))
for p,_ in products:
    tot = sum(cnt[p].values()); tsa = sum(top[p].values())
    L.append(f'| {p} | ' + ' | '.join(f'{cnt[p][i]} ({top[p][i]})' if cnt[p][i] else '—' for i in inds) + f' | **{tot} ({tsa})** |')
L.append('\n## 2. 제품별 S등급(최우선) 유닛\n')
for p,_ in products:
    if sunits[p]:
        L.append(f'### {p}')
        for s in sunits[p]: L.append(f'- {s}')
        L.append('')
open(os.path.join(out, '05_제품별_적용시장_분석.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print(len(files), len(rows))
for p,_ in products: print(p, sum(cnt[p].values()), sum(top[p].values()), len(sunits[p]))
