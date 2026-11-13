# Atualiza vendas/index.html com as vendas da aba "contador de vendas".
# uso (na raiz do repo): python3 tools/vendas_atualizar.py < consultas.txt
# consultas.txt = texto (get_page_text) de 4 consultas gviz à aba, cada uma depois de uma linha marcadora:
#   ## SW  -> select A,S,T,U,W where A is not null and (U >= date 'INICIO' or W >= date 'INICIO')
#   ## D   -> select A,D (mesmo where)      ## P -> select A,P (mesmo where)      ## M -> select A,M (mesmo where)
# INICIO = primeiro mês do calendário (DADOS.inicio, hoje 2026-09-01).
# Regras do usuário: 1) se o mês da confirmação (W) existir, a venda conta nesse mês; senão no mês da venda (U);
# 2) o placar mostra o mês vigente (o calendário mostra os outros); 3) com FID (S) = Comercial;
# 4) sem FID = Facilitada; 5) Data Confirmação Venda 2.0 (T) em branco = Facilitada.
import re, sys, json
sys.path.insert(0, 'tools'); from comum import *
P = 'vendas/index.html'
txt = sys.stdin.read()
partes, atual = {}, None
for l in txt.splitlines():
    m = re.match(r'\s*##\s*(SW|D|P|M)\b', l)
    if m: atual = m.group(1); partes[atual] = {}; continue
    m = re.match(r'\s*(OP-\d+)\s+(.*?)\s*$', l)
    if m and atual: partes[atual][m.group(1)] = m.group(2)
for k in ('SW', 'D', 'P', 'M'):
    if k not in partes: sys.exit('faltou a consulta ## ' + k)
base = base_corretores()
DONO = {'MADELEINE BORGES': 'Mada', 'BRUNO MICCOLI DE OLIVEIRA': 'Bruno', 'ALDINEI REZENDE FAGUNDES': 'Aldinei', 'ICARO ZIVKO MIRANDA': 'Ícaro',
        'IVAN DE AGUIAR NASCIMENTO': 'Ivan', 'SHIRLEY DO NASCIMENTO PINA': 'Pina', 'SANDRO ANTONIO DA SILVA': 'Sandro', 'LAIS SILVA BASTOS PASLAUSKI': 'Lais',
        'GIANLUCCA VASCONCELOS PUGLIESI': 'Gianlucca', 'ARTHUR SIMAS ANDRIACA': 'Arthur'}
GR = {'Aldinei': 'Takeashi', 'Ícaro': 'Takeashi', 'Pina': 'Takeashi', 'Mada': 'Patricia', 'Bruno': 'Patricia', 'Sandro': 'Patricia', 'Ivan': 'Gustavo', 'Débora': 'Gustavo'}
s0 = open(P).read()
inicio = re.search(r'  inicio: "(\d{4}-\d{2})"', s0).group(1)
def mes(txt):
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', txt or '')
    if not m or int(m.group(3)) > 2100: return None
    return f'{m.group(3)}-{int(m.group(2)):02d}'
D8 = r'\d{1,2}/\d{1,2}/\d{4}'
vendas, ruins = [], []
for op, resto in partes['SW'].items():
    m = re.fullmatch(rf'(?:([\d.]+)\s+)?(?:({D8})\s+)?({D8})\s+({D8})', resto)
    if not m: ruins.append(op); continue
    fid, t, u, w = m.groups()
    ym = mes(w) or mes(u)
    if not ym or ym < inicio: continue
    tipo = 'Comercial' if fid and t else 'Facilitada'
    dono = partes['D'].get(op, '')
    gv = DONO.get(norm(dono), dono.split()[0].title() if dono else '?')
    v = {'mes': ym, 'nome': nome_bonito(partes['P'].get(op, '?'), base), 'gv': gv, 'projeto': partes['M'].get(op, '?'), 'tipo': tipo}
    if gv in GR: v['gr'] = GR[gv]
    vendas.append(v)
if ruins: print('linhas que não consegui ler:', ruins)
vendas.sort(key=lambda v: (v['mes'], v['gv'], v['nome']))
s = s0
ini = s.index('  vendas: [\n'); fim = s.index('\n  ]\n};', ini)
antes = s[ini:fim]
novo = '  vendas: [\n' + ',\n'.join('    ' + json.dumps(v, ensure_ascii=False) for v in vendas)
vig = agora().strftime('%Y-%m')
mudou = antes != novo
s = s[:ini] + novo + s[fim:]
s = re.sub(r'  mes: "[^"]+",', f'  mes: "{vig}",', s, count=1)
s = re.sub(r'  atualizado: "[^"]+",', f'  atualizado: "{agora().strftime("%Y-%m-%dT%H:%M:00-03:00")}",', s, count=1)
open(P, 'w').write(s)
from collections import Counter
c = Counter((v['mes'], v['tipo']) for v in vendas)
print('vendas mudaram' if mudou else 'vendas sem mudança')
for k in sorted({v['mes'] for v in vendas}):
    if k >= '2026-09': print(k, c[(k, 'Comercial')] + c[(k, 'Facilitada')], 'com', c[(k, 'Comercial')], 'fac', c[(k, 'Facilitada')])
