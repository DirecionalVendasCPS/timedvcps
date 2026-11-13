# Atualiza conversao/index.html (Conversão Visitas x Agendamentos).
# uso (na raiz do repo, depois de tools/agend_hoje.py): python3 tools/conv_atualizar.py < visitas.txt
# visitas.txt = texto do gviz da aba "agendamentos normal" com as linhas que têm a coluna H
#   (Data de comparecimento) preenchida, desde o início do trimestre:
#   select A,K where A >= date 'AAAA-MM-01' and H is not null and K contains 'Corretor(a)'
# Agendamentos = todas as linhas criadas no mês (mesma contagem da página Agendamentos do dia).
# Visitas = linhas criadas no mês com a coluna H preenchida.
import re, sys, json, collections
sys.path.insert(0, 'tools'); from comum import *
P = 'conversao/index.html'
base = base_corretores()
ag = open('agendamentos/index.html').read()
dias = json.loads(re.search(r'  dias: (\{.*\}),\n', ag).group(1))
equipe = re.search(r'  equipe: \[\n(.*?)\n  \],', ag, re.S).group(1)
meses = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for d, v in dias.items():
    for n, q in v.items(): meses[d[:7]][n][0] += q
nvis = 0
for l in sys.stdin.read().splitlines():
    m = re.match(r'\s*(\d{1,2})/(\d{1,2})/(\d{4})\b.*?Corretor\(a\)\s+(.+?)\s*$', l)
    if not m: continue
    d, mo, a, nome = m.groups()
    meses[f'{a}-{int(mo):02d}'][nome_bonito(nome, base)][1] += 1; nvis += 1
out = {k: dict(sorted(v.items())) for k, v in sorted(meses.items())}
s = open(P).read()
s = re.sub(r'  meses: \{.*\},\n', lambda _: '  meses: ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ',\n', s, count=1)
s = re.sub(r'  equipe: \[\n.*?\n  \],', lambda _: '  equipe: [\n' + equipe + '\n  ],', s, count=1, flags=re.S)
s = re.sub(r'  mes: "[^"]+",', f'  mes: "{agora().strftime("%Y-%m")}",', s, count=1)
s = re.sub(r'  atualizado: "[^"]+",', f'  atualizado: "{agora().strftime("%Y-%m-%dT%H:%M:00-03:00")}",', s, count=1)
open(P, 'w').write(s)
for k, v in out.items():
    a, b = sum(x[0] for x in v.values()), sum(x[1] for x in v.values())
    print(k, 'agendamentos', a, 'visitas', b, f'conversão {b/a*100:.1f}%' if a else '')
    bad = [n for n, x in v.items() if x[1] > x[0]]
    if bad: print('  ATENÇÃO visitas > agendamentos:', bad)
print('linhas de visita lidas:', nvis)
