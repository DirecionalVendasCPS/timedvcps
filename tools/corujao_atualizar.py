# Atualiza o placar do corujão (corujao/index.html) com os agendamentos criados no dia do corujão.
# uso (na raiz do repo): python3 tools/corujao_atualizar.py "DD/MM/AAAA HH:MM" < linhas.txt
# linhas.txt = texto do gviz da aba Agendamentos: select A,E,J where A = date 'DIA DO CORUJÃO'
#   (cada linha "dd/mm/aaaa dd/mm/aaaa NOME": criação, data agendada, corretor)
# - Só contam agendamentos criados no dia (DADOS.dia) com data agendada até DADOS.ate (regra do grupo, ex.: até domingo).
# - feito de cada promessa = agendamentos do corretor da lista (equipe[].lista); quem não prometeu e agendou vai para "extras".
import re, sys, json
sys.path.insert(0, 'tools'); from comum import *
P = 'corujao/index.html'
s = open(P).read()
a = s.index('const DADOS = {'); b = s.index('\n};', a)
bloco = s[a:b]
dia = re.search(r'  dia: "([^"]+)"', bloco).group(1)
ate = (re.search(r'  ate: "([^"]+)"', bloco) or re.search(r'  dia: "([^"]+)"', bloco)).group(1)
equipe = re.findall(r'\{nome: "([^"]+)", gv: "[^"]+", gr: "[^"]+", lista: (?:"([^"]+)"|null)\}', bloco)
por_nome = {norm(n): (n, l) for n, l in equipe}
base = base_corretores()
cont, fora = {}, {}
for l in sys.stdin.read().splitlines():
    m = re.match(r'\s*(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2})/(\d{1,2})/(\d{4})\s+(.+?)\s*$', l)
    if not m: continue
    d, mo, y, d2, mo2, y2, nome = m.groups()
    if f'{y}-{int(mo):02d}-{int(d):02d}' != dia or f'{y2}-{int(mo2):02d}-{int(d2):02d}' > ate: continue
    nb = nome_bonito(nome, base)
    n, lista = por_nome.get(norm(nb), (nb, None))
    if lista: cont[lista] = cont.get(lista, 0) + 1
    else: fora[n] = fora.get(n, 0) + 1
def troca_feito(m):
    return '{nome: "%s", prometido: %s, feito: %d}' % (m.group(1), m.group(2), cont.get(m.group(1), 0))
novo = re.sub(r'\{nome: "([^"]+)", prometido: (\d+), feito: \d+\}', troca_feito, bloco)
ex = ',\n'.join('    {nome: %s, feito: %d}' % (json.dumps(n, ensure_ascii=False), v) for n, v in sorted(fora.items()))
novo = re.sub(r'  extras: \[.*?\n  \]', '  extras: [\n' + ex + '\n  ]', novo, flags=re.S)
novo = re.sub(r'  atualizado: "[^"]+"', '  atualizado: "%s"' % agora().strftime('%Y-%m-%dT%H:%M:00-03:00'), novo)
novo = re.sub(r'  refresh: "[^"]*"', '  refresh: "%s"' % sys.argv[1], novo)
s = s[:a] + novo + s[b:]
open(P, 'w').write(s)
print('corujão', dia, '| promessas:', cont, '| extras:', fora)

# placar do dia também no calendário (corujao/datas.js)
prom = sum(int(x) for x in re.findall(r'\{nome: "[^"]+", prometido: (\d+), feito: \d+\}', novo))
feito_tot = sum(cont.values()) + sum(fora.values())
D = 'corujao/datas.js'; ds = open(D).read()
ds = re.sub(r'  \{dia: "%s", rotulo: "([^"]+)"[^}]*\}' % dia, lambda m: '  {dia: "%s", rotulo: "%s", feito: %d, prometido: %d, placar: "%d/%d"}' % (dia, m.group(1), feito_tot, prom, feito_tot, prom), ds)
open(D, 'w').write(ds)
