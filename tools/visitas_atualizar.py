# Atualiza visitas/index.html (Visitas do dia), com a mesma estrutura da página de agendamentos.
# uso (na raiz do repo, depois de base_atualizar.py): python3 tools/visitas_atualizar.py "DD/MM HH:MM" < visitas_dia.txt
# visitas_dia.txt = saída do gviz da planilha "BURDIM - Gestão Semanal - GVs - CAMPINAS", aba Visitas (gid=636908934):
#   select K,I,count(A) where K >= date 'AAAA-MM-DD' group by K,I      (K = Data de comparecimento, I = corretor)
#   linhas no formato "AAAA-M-D NOME DO CORRETOR quantidade". A página é refeita inteira a partir do início indicado.
# O argumento é o horário do último refresh dessa planilha (Auto Refresh Execution Log).
import re, sys, json, collections
sys.path.insert(0, 'tools'); from comum import *
P = 'visitas/index.html'
base = base_corretores()
dias = collections.defaultdict(lambda: collections.Counter())
n = 0
for l in sys.stdin.read().splitlines():
    m = re.match(r'\s*(\d{4})-(\d{1,2})-(\d{1,2})\s+(.+?)\s+(\d+)\s*$', l)
    if not m: continue
    a, mo, d, nome, q = m.groups()
    dias[f'{a}-{int(mo):02d}-{int(d):02d}'][nome_bonito(nome, base)] += int(q); n += int(q)
out = {k: dict(sorted(v.items())) for k, v in sorted(dias.items())}
equipe = re.search(r'  equipe: \[\n(.*?)\n  \],', open('agendamentos/index.html').read(), re.S).group(1)
s = open(P).read()
s = re.sub(r'  dias: \{.*\},\n', lambda _: '  dias: ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ',\n', s, count=1)
s = re.sub(r'  equipe: \[\n.*?\n  \],', lambda _: '  equipe: [\n' + equipe + '\n  ],', s, count=1, flags=re.S)
s = re.sub(r'  hoje: "[^"]+",', f'  hoje: "{agora().strftime("%Y-%m-%d")}",', s, count=1)
s = re.sub(r'  atualizado: "[^"]+",', f'  atualizado: "{agora().strftime("%Y-%m-%dT%H:%M:00-03:00")}",', s, count=1)
if len(sys.argv) > 1: s = re.sub(r'  refresh: "[^"]*",', f'  refresh: "{sys.argv[1]}",', s, count=1)
open(P, 'w').write(s)
hoje = agora().strftime('%Y-%m-%d')
print('visitas lidas:', n, '| dias:', len(out), '| hoje:', sum(out.get(hoje, {}).values()))
