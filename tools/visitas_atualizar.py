# Atualiza visitas/index.html (Visitas do dia), com a mesma estrutura da página de agendamentos.
# uso (na raiz do repo, depois de base_atualizar.py):
#   python3 tools/visitas_atualizar.py "DD/MM HH:MM" agendados.txt < visitas_dia.txt
# visitas_dia.txt = visitas realizadas, planilha "BURDIM - Gestão Semanal - GVs - CAMPINAS", aba Agendamentos (gid=885964070):
#   select E,J,count(A) where E >= date 'AAAA-MM-DD' and H = true group by E,J   (E = Data, J = corretor, H = Visita Realizada)
#   linhas no formato "AAAA-M-D NOME DO CORRETOR quantidade". A página é refeita inteira a partir do início indicado.
# agendados.txt = visitas agendadas para cada dia (vermelho na página), aba Agendamentos (gid=885964070):
#   select E,J,count(A) where E >= date 'AAAA-MM-DD' group by E,J      (E = Data agendada, J = corretor)
# O 1º argumento é o horário do último refresh dessa planilha (Auto Refresh Execution Log), ex.: "15/11/2026 17:47".
import re, sys, json, collections
sys.path.insert(0, 'tools'); from comum import *
P = 'visitas/index.html'
base = base_corretores()
def ler(texto):
    dias, n = collections.defaultdict(lambda: collections.Counter()), 0
    for l in texto.splitlines():
        m = re.match(r'\s*(\d{4})-(\d{1,2})-(\d{1,2})\s+(.+?)\s+(\d+)\s*$', l)
        if not m: continue
        a, mo, d, nome, q = m.groups()
        dias[f'{a}-{int(mo):02d}-{int(d):02d}'][nome_bonito(nome, base)] += int(q); n += int(q)
    return {k: dict(sorted(v.items())) for k, v in sorted(dias.items())}, n
out, n = ler(sys.stdin.read())
ag, nag = ler(open(sys.argv[2]).read()) if len(sys.argv) > 2 else (None, 0)
equipe = re.search(r'  equipe: \[\n(.*?)\n  \],', open('agendamentos/index.html').read(), re.S).group(1)
s = open(P).read()
s = re.sub(r'  dias: \{.*\},\n', lambda _: '  dias: ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ',\n', s, count=1)
if ag is not None: s = re.sub(r'  agendados: \{.*\},\n', lambda _: '  agendados: ' + json.dumps(ag, ensure_ascii=False, separators=(',', ':')) + ',\n', s, count=1)
s = re.sub(r'  equipe: \[\n.*?\n  \],', lambda _: '  equipe: [\n' + equipe + '\n  ],', s, count=1, flags=re.S)
s = re.sub(r'  hoje: "[^"]+",', f'  hoje: "{agora().strftime("%Y-%m-%d")}",', s, count=1)
s = re.sub(r'  atualizado: "[^"]+",', f'  atualizado: "{agora().strftime("%Y-%m-%dT%H:%M:00-03:00")}",', s, count=1)
if len(sys.argv) > 1: s = re.sub(r'  refresh: "[^"]*",', f'  refresh: "{sys.argv[1]}",', s, count=1)
open(P, 'w').write(s)
hoje = agora().strftime('%Y-%m-%d')
print('visitas realizadas lidas:', n, '| hoje:', sum(out.get(hoje, {}).values()), '| agendadas lidas:', nag, '| agendadas para hoje:', sum((ag or {}).get(hoje, {}).values()))
