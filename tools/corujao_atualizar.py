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

# placar do dia também no calendário e no comparativo por GR (corujao/datas.js)
prom = sum(int(x) for x in re.findall(r'\{nome: "[^"]+", prometido: (\d+), feito: \d+\}', novo))
feito_tot = sum(cont.values()) + sum(fora.values())
gr_de = {norm(n): g for n, g in re.findall(r'\{nome: "([^"]+)", gv: "[^"]+", gr: "([^"]+)"', novo)}
gr_lista = {l: g for n, g, l in re.findall(r'\{nome: "([^"]+)", gv: "[^"]+", gr: "([^"]+)", lista: "([^"]+)"\}', novo)}
gr_lista.update({'Vanessa': 'Takeashi'})  # fora da base (mesma regra da roleta)
grs = {}
for n, pr in re.findall(r'\{nome: "([^"]+)", prometido: (\d+), feito: \d+\}', novo):
    g = gr_lista.get(n)
    if g: grs.setdefault(g, [0, 0]); grs[g][0] += cont.get(n, 0); grs[g][1] += int(pr)
for n, v in fora.items():
    g = gr_de.get(norm(n))
    if g: grs.setdefault(g, [0, 0]); grs[g][0] += v
ordem = ['Takeashi', 'Patricia', 'Gustavo']
gtxt = ', '.join('%s: [%d, %d]' % (g, *grs.get(g, [0, 0])) for g in ordem)
D = 'corujao/datas.js'; ds = open(D).read()
ds = re.sub(r'  \{dia: "%s", rotulo: "([^"]+)".*\}(?=,?\n)' % dia, lambda m: '  {dia: "%s", rotulo: "%s", feito: %d, prometido: %d, placar: "%d/%d", gr: {%s}}' % (dia, m.group(1), feito_tot, prom, feito_tot, prom, gtxt), ds)
open(D, 'w').write(ds)
print('por GR:', gtxt)
# muda a versão do datas.js nas páginas para o navegador não usar o calendário/comparativo antigo do cache
import glob
v = agora().strftime('%Y%m%d%H%M')
for f in glob.glob('corujao/*.html'):
    t = open(f).read(); t2 = re.sub(r'src="datas\.js(\?v=\w+)?"', 'src="datas.js?v=%s"' % v, t)
    if t2 != t: open(f, 'w').write(t2)
