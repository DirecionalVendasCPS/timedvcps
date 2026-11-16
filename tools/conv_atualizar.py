# Atualiza conversao/index.html (Conversão Visitas x Agendamentos).
# uso (na raiz do repo, DEPOIS de tools/visitas_atualizar.py): python3 tools/conv_atualizar.py
#   (não lê mais nada da entrada; se receber texto pela entrada, ignora)
# Base = a mesma da página Visitas do dia: planilha "BURDIM - Gestão Semanal - GVs - CAMPINAS", aba "Agendamentos":
#   Agendamentos = linhas com a Data (coluna E) no dia (DADOS.agendados de visitas/index.html).
#   Visitas      = dessas, as com Visita Realizada (coluna H) = true (DADOS.dias de visitas/index.html).
#   Conversão    = visitas ÷ agendamentos.
# Só entram os dias até hoje (agendamentos de dias que ainda não chegaram ficam de fora).
# Grava dias: {"AAAA-MM-DD": {"Nome": [agendamentos, visitas]}} e meses: {"AAAA-MM": {"Nome": [agendamentos, visitas]}}.
import re, sys, json, collections
sys.path.insert(0, 'tools'); from comum import *
P = 'conversao/index.html'
vis = open('visitas/index.html').read()
def bloco(nome):
    return json.loads(re.search(r'  ' + nome + r': (\{.*\}),\n', vis).group(1))
agendados, realizadas = bloco('agendados'), bloco('dias')
hoje = re.search(r'  hoje: "([^"]+)"', vis).group(1)
refresh = re.search(r'  refresh: "([^"]*)"', vis).group(1)
equipe = re.search(r'  equipe: \[\n(.*?)\n  \],', vis, re.S).group(1)

pordia = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for d, v in agendados.items():
    if d <= hoje:
        for n, q in v.items(): pordia[d][n][0] += q
for d, v in realizadas.items():
    if d <= hoje:
        for n, q in v.items(): pordia[d][n][1] += q
meses = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for d, v in pordia.items():
    for n, (a, b) in v.items(): meses[d[:7]][n][0] += a; meses[d[:7]][n][1] += b
outd = {k: dict(sorted(v.items())) for k, v in sorted(pordia.items())}
out = {k: dict(sorted(v.items())) for k, v in sorted(meses.items())}

s = open(P).read()
s = re.sub(r'  dias: \{.*\},\n', lambda _: '  dias: ' + json.dumps(outd, ensure_ascii=False, separators=(',', ':')) + ',\n', s, count=1)
s = re.sub(r'  meses: \{.*\},\n', lambda _: '  meses: ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ',\n', s, count=1)
s = re.sub(r'  equipe: \[\n.*?\n  \],', lambda _: '  equipe: [\n' + equipe + '\n  ],', s, count=1, flags=re.S)
s = re.sub(r'  mes: "[^"]+",', f'  mes: "{hoje[:7]}",', s, count=1)
s = re.sub(r'  atualizado: "[^"]+",', f'  atualizado: "{agora().strftime("%Y-%m-%dT%H:%M:00-03:00")}",', s, count=1)
s = re.sub(r'  refresh: "[^"]*",', lambda _: f'  refresh: "{refresh}",', s, count=1)
open(P, 'w').write(s)
for k, v in out.items():
    a, b = sum(x[0] for x in v.values()), sum(x[1] for x in v.values())
    print(k, 'agendamentos', a, 'visitas', b, f'conversão {b/a*100:.1f}%' if a else '')
    bad = [n for n, x in v.items() if x[1] > x[0]]
    if bad: print('  ATENÇÃO visitas > agendamentos:', bad)
print('dias até', hoje, '| dados da planilha de gestão:', refresh)
