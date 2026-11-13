# Atualiza agendamentos/index.html com os agendamentos lidos da aba "agendamentos normal".
# uso (na raiz do repo): python3 tools/agend_hoje.py < linhas.txt
# linhas.txt = texto do gviz (get_page_text) com linhas "dd/mm/aaaa ... - Corretor(a) NOME".
# Os dias que aparecem no texto são substituídos inteiros; os outros dias ficam como estão.
import re, sys, json, collections
sys.path.insert(0, 'tools'); from comum import *
P = 'agendamentos/index.html'
txt = sys.stdin.read()
base = base_corretores()
dias = collections.defaultdict(collections.Counter)
for l in txt.splitlines():
    m = re.match(r'\s*(\d{1,2})/(\d{1,2})/(\d{4})\b.*?Corretor\(a\)\s+(.+?)\s*$', l)
    if not m: continue
    d, mo, a, nome = m.groups()
    dias[f'{a}-{int(mo):02d}-{int(d):02d}'][nome_bonito(nome, base)] += 1
s = open(P).read()
mm = re.search(r'  dias: (\{.*\}),\n', s)
atual = json.loads(mm.group(1))
hoje = agora().strftime('%Y-%m-%d')
antes = {k: sum(v.values()) for k, v in atual.items() if k in dias or k == hoje}
for k, v in dias.items(): atual[k] = dict(sorted(v.items()))
atual = dict(sorted(atual.items()))
s = s[:mm.start(1)] + json.dumps(atual, ensure_ascii=False, separators=(',', ':')) + s[mm.end(1):]
s = re.sub(r'  hoje: "[^"]+",', f'  hoje: "{hoje}",', s, count=1)
s = re.sub(r'  atualizado: "[^"]+",', f'  atualizado: "{agora().strftime("%Y-%m-%dT%H:%M:00-03:00")}",', s, count=1)
open(P, 'w').write(s)
for k in sorted(set(dias) | {hoje}):
    print(k, antes.get(k, 0), '->', sum(atual.get(k, {}).values()))
