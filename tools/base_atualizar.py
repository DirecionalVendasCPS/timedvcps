# Aplica a aba "base de corretores" às páginas (rodar na raiz do repo).
# uso: python3 tools/base_atualizar.py < base.txt
# base.txt = texto (get_page_text) da consulta gviz à aba "base de corretores" (gid=232753372):
#   select A,L,N,AI where A is not null   -> "NOME STATUS dd/mm/aaaa GR (nome completo do proprietário da conta)"
# - agendamentos/index.html: a lista de corretores (equipe) passa a ter só os ATIVOS (status Ativo ou Reativado).
#   A equipe (GV) de cada um vem de tools/gv.json (nome -> GV); quem não estiver lá entra como "A definir".
#   O GR vem da base (coluna AI).
# - calendario/index.html: aniversários dos corretores ativos (só dia e mês; o ano de nascimento não é publicado).
import re, sys, json
sys.path.insert(0, 'tools'); from comum import *
ATIVOS = {'ATIVO', 'REATIVADO'}
GRS = {'TAKEASHI': 'Takeashi', 'PATRICIA': 'Patricia', 'GUSTAVO': 'Gustavo'}
gvmap = {norm(k): v for k, v in json.load(open('tools/gv.json')).items()}
linhas, ignorados = [], []
for l in sys.stdin.read().splitlines():
    m = re.match(r'\s*(.+?)\s+(\S+)\s+(\d{1,2})/(\d{1,2})/(\d{4})\s+(.+?)\s*$', l)
    if not m: continue
    nome, status, d, mo, _, dono = m.groups()
    if norm(status) not in ATIVOS: ignorados.append((nome, status)); continue
    gr = next((v for k, v in GRS.items() if k in norm(dono)), dono.split()[0].title())
    linhas.append((nome, gr, f'{int(mo):02d}-{int(d):02d}'))
if len(linhas) < 10: sys.exit('base com poucos corretores ativos (%d) — nada foi alterado' % len(linhas))
base_antiga = base_corretores()
def bonito(n):
    k = ALIAS.get(norm(n), norm(n))
    if k in base_antiga: return base_antiga[k][0]
    return ' '.join(w.lower() if w.lower() in ('de', 'da', 'do', 'dos', 'das') else w[:1].upper() + w[1:].lower() for w in n.split())
equipe, aniv, novos = [], [], []
for nome, gr, dm in linhas:
    nb = bonito(nome)
    gv = gvmap.get(ALIAS.get(norm(nome), norm(nome))) or gvmap.get(norm(nb))
    if not gv: gv = 'A definir'; novos.append(nb)
    equipe.append((nb, gv, gr))
    aniv.append({'nome': nb, 'dia': dm})
ORD_GR = {'Takeashi': 0, 'Patricia': 1, 'Gustavo': 2}
equipe.sort(key=lambda e: (ORD_GR.get(e[2], 9), e[1] == 'A definir', e[1], e[0]))
# agendamentos: troca o bloco equipe
P = 'agendamentos/index.html'; s = open(P).read()
a = s.index('  equipe: [\n'); b = s.index('\n  ]', a)
antes = {n for n, _, _ in re.findall(r'\{nome: "([^"]+)", gv: "([^"]+)", gr: "([^"]+)"\}', s[a:b])}
txt = '  equipe: [\n' + ',\n'.join(f'    {{nome: {json.dumps(n, ensure_ascii=False)}, gv: {json.dumps(g, ensure_ascii=False)}, gr: {json.dumps(r, ensure_ascii=False)}}}' for n, g, r in equipe)
s = s[:a] + txt + s[b:]
open(P, 'w').write(s)
# calendário: troca o bloco ANIVERSARIOS
P2 = 'calendario/index.html'; c = open(P2).read()
aniv.sort(key=lambda x: (x['dia'], x['nome']))
bloco = 'const ANIVERSARIOS = [\n' + ',\n'.join('  ' + json.dumps(x, ensure_ascii=False) for x in aniv) + '\n];'
c = re.sub(r'const ANIVERSARIOS = \[.*?\n\];', lambda m: bloco, c, count=1, flags=re.S)
open(P2, 'w').write(c)
depois = {n for n, _, _ in equipe}
print('corretores ativos:', len(equipe), '| saíram:', sorted(antes - depois), '| entraram:', sorted(depois - antes))
if novos: print('sem equipe (GV) cadastrada em tools/gv.json:', novos)
if ignorados: print('fora (status):', ignorados)
