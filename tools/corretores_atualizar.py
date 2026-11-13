# Atualiza corretores/index.html (Gestão Semanal dos Corretores: funil 60 OPs → 30 AG → 10 VIS → 4 PAS → 1 venda).
# uso (na raiz do repo, depois de base_atualizar.py e vendas_atualizar.py):
#   python3 tools/corretores_atualizar.py "dd/mm/aaaa hh:mm do refresh" < semanas.txt
# semanas.txt: blocos "## ETAPA AAAA-MM-DD" (ETAPA = OPS, AG, VIS ou PAS; data = domingo que inicia a semana)
#   seguidos de linhas "NOME DO CORRETOR quantidade" (saída do gviz com group by, planilha
#   "BURDIM - Gestão Semanal - GVs - CAMPINAS": abas Oportunidades, Agendamentos, Visitas e Pastas).
# Só entram os corretores ativos (lista da página de agendamentos, que vem da aba "base de corretores").
# Vendas do mês: as mesmas do Contador de vendas (vendas/index.html), por corretor.
import re, sys, json, collections
sys.path.insert(0, 'tools'); from comum import *
P = 'corretores/index.html'
base = base_corretores()
ativos = {v[0] for v in base.values()}
mes = agora().strftime('%Y-%m')
dados = collections.defaultdict(lambda: collections.defaultdict(dict))
semanas, fora, cur = set(), collections.Counter(), None
for l in sys.stdin.read().splitlines():
    l = l.strip()
    m = re.match(r'##\s*(OPS|AG|VIS|PAS)\s+(\d{4}-\d{2}-\d{2})', l)
    if m: cur = (m.group(1).lower(), m.group(2)); semanas.add(m.group(2)); continue
    m = re.match(r'(.+?)\s+(\d+)$', l)
    if not m or not cur: continue
    nome = nome_bonito(m.group(1), base)
    if nome not in ativos: fora[nome] += int(m.group(2)); continue
    et, sem = cur
    dados[nome][et][sem] = dados[nome][et].get(sem, 0) + int(m.group(2))
semanas = sorted(semanas)
out = {n: {et: [dados[n][et].get(s, 0) for s in semanas] for et in ('ops', 'ag', 'vis', 'pas')} for n in sorted(dados)}
vs = open('vendas/index.html').read()
vendas = collections.Counter(nome_bonito(n, base) for n in re.findall(r'\{"mes": "' + mes + r'", "nome": "([^"]+)"', vs))
equipe = re.search(r'  equipe: \[\n(.*?)\n  \],', open('agendamentos/index.html').read(), re.S).group(1)
refresh = sys.argv[1] if len(sys.argv) > 1 else ''
s = open(P).read()
s = re.sub(r'  semanas: \[.*\],\n', lambda _: '  semanas: ' + json.dumps(semanas) + ',\n', s, count=1)
s = re.sub(r'  dados: \{.*\},\n', lambda _: '  dados: ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ',\n', s, count=1)
s = re.sub(r'  vendas: \{.*\},\n', lambda _: '  vendas: ' + json.dumps(dict(vendas), ensure_ascii=False) + ',\n', s, count=1)
s = re.sub(r'  equipe: \[\n.*?\n  \],', lambda _: '  equipe: [\n' + equipe + '\n  ],', s, count=1, flags=re.S)
s = re.sub(r'  mes: "[^"]+",', f'  mes: "{mes}",', s, count=1)
s = re.sub(r'  refresh: "[^"]*",', f'  refresh: "{refresh}",', s, count=1)
s = re.sub(r'  atualizado: "[^"]+",', f'  atualizado: "{agora().strftime("%Y-%m-%dT%H:%M:00-03:00")}",', s, count=1)
open(P, 'w').write(s)
tot = {et: sum(sum(v[et]) for v in out.values()) for et in ('ops', 'ag', 'vis', 'pas')}
print('semanas:', semanas, '| ativos com dados:', len(out), 'de', len(ativos), '| totais:', tot, '| vendas:', dict(vendas))
if fora: print('fora da base de ativos (ignorados):', dict(fora))
