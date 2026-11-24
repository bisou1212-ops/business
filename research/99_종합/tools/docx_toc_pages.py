import sys, json, subprocess, re
S = sys.argv[1]
titles = json.load(open(S + '/titles.json', encoding='utf-8'))
n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', S + '/test.pdf'], capture_output=True, text=True).stdout).group(1))
def page_text(i):
    t = subprocess.run(['pdftotext', '-f', str(i), '-l', str(i), S + '/test.pdf', '-'], capture_output=True, text=True).stdout
    t = re.sub(r'\s', '', t)
    return re.sub(r'2027산업·시장·자동화장비종합심층조사\|\d+', '', t)  # drop footer
txt = [page_text(i) for i in range(1, n + 1)]
res, start = [], 3
for t in titles:
    k = re.sub(r'\s', '', t)[:24]
    pg = next(i + 1 for i in range(start - 1, n) if txt[i].startswith(k) or k in txt[i][:200])
    res.append([t, pg]); start = pg + 1
json.dump(res, open(S + '/toc.json', 'w', encoding='utf-8'), ensure_ascii=False)
print([r[1] for r in res])
