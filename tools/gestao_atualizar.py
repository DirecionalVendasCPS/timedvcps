# Atualiza gestao/index.html (Gestão Semanal dos GVs) com a aba "Novembro/26" e a aba "Calc_Data"
# da planilha "BURDIM - Gestão Semanal - GVs - CAMPINAS".
# uso (na raiz do repo): python3 tools/gestao_atualizar.py "DD/MM HH:MM" mes.txt < calc.txt
#   mes.txt  = get_page_text de .../gviz/tq?tqx=out:html&sheet=Novembro/26
#   calc.txt = get_page_text de .../gviz/tq?tqx=out:html&sheet=Calc_Data
# - Realizado: bloco "Realizado Semanal" (uma linha por GV: nome curto, GR, 4 grupos OPs/AG/VIS/PAS com
#   6 semanas + % + 2 totais, depois 6 semanas de vendas). Usa as 5 primeiras semanas (01/11 a 29/11).
# - Regra do usuário: as vendas migradas de meses anteriores (lançadas em 10/11) NÃO contam: 10 da Mada e 2 do Bruno, semana 08/11.
# - Tendência: semanas de novembro da Calc_Data (OPs AG VIS PAS VN), com a mesma regra das vendas migradas na semana 08/11.
# - Empreendimentos e origens: contagens da Calc_Data (só as que têm venda).
import re, sys, json
sys.path.insert(0, 'tools'); from comum import *
P = 'gestao/index.html'
SEM = ["2026-11-01", "2026-11-08", "2026-11-15", "2026-11-22", "2026-11-29"]
MIG = {"Mada": 10, "Bruno": 2}  # vendas de 10/11 migradas de meses anteriores (aba Vendas: Mada 10, Bruno 2)
NOME = {"Icaro": "Ícaro", "Debora": "Débora"}
GRS = ("Takeashi", "Patricia", "Gustavo")
mes = open(sys.argv[2], encoding='utf-8').read()
calc = sys.stdin.read()
s = open(P, encoding='utf-8').read()
m = re.search(r'const DADOS = (\{.*?\});\n', s)
D = json.loads(m.group(1))

bloco = mes.split("Realizado Semanal", 1)[1].split("Meta GRs", 1)[0]
real, tot = [], {k: 0 for k in ("ops", "ag", "vis", "pas", "vn")}
for l in bloco.splitlines():
    t = l.split()
    gi = next((i for i, x in enumerate(t) if x in GRS and i > 0), None)
    if gi is None: continue
    gv = NOME.get(t[gi - 1], t[gi - 1]); gr = t[gi]; v = t[gi + 1:]
    g, i = {}, 0
    for k in ("ops", "ag", "vis", "pas"):
        g[k] = [int(x) for x in v[i:i + 6]]; i += 9
    g["vn"] = [int(x) for x in v[i:i + 6]]
    g["vn"][1] = max(0, g["vn"][1] - MIG.get(gv, 0))
    for w in range(5):
        real.append({"gv": gv, "gr": gr, "semana": SEM[w], **{k: g[k][w] for k in g}})
    for k in g: tot[k] += sum(g[k])
if len(real) < 5 * 6: sys.exit("realizado: poucas linhas lidas (%d) — nada mudado" % len(real))
gvs_meta = {x["gv"] for x in D["metas"]}
novos = {r["gv"] for r in real} - gvs_meta
if novos: print("GVs na planilha sem meta na página (ignorados):", novos)
D["realizado"] = [r for r in real if r["gv"] in gvs_meta]

T = {t["semana"]: t for t in D["tendencia"]}
for mm in re.finditer(r'^(\d\d)/(11) (\d+) (\d+) (\d+) (\d+) (\d+) ', calc, re.M):
    sem = "2026-%s-%s" % (mm.group(2), mm.group(1))
    ops, ag, vis, pas, vn = map(int, mm.groups()[2:])
    if sem == "2026-11-08": vn = max(0, vn - sum(MIG.values()))
    if sem in SEM and (ops or ag or vis or pas or vn or sem in T):
        T[sem] = {"semana": sem, "ops": ops, "ag": ag, "vis": vis, "pas": pas, "vn": vn}
hoje_sem = max(x for x in T if any(T[x][k] for k in ("ops", "vis", "pas")))
D["tendencia"] = sorted((T[x] for x in T if x <= hoje_sem), key=lambda t: t["semana"])[-6:]

EMP = ["Alta Vista Mangará", "Cores da Mata Mangará", "Seleto Amoreiras", "Rise Parque Prado", "Casa Prado Residencial Riva",
       "Compra e Venda de Bens Imóveis III - SP"]
ORI = ["WhatsApp", "Oferta do corretor", "Stand", "Lead ADS", "DV ON", "Indica mais", "Book", "Cadastre-se", "Portal Vertical"]
def contar(nomes):
    out = []
    for n in nomes:
        mm = re.search(re.escape(n) + r' (\d+) [0-9,]+', calc)
        if mm and int(mm.group(1)) > 0: out.append((n, int(mm.group(1))))
    return out
e, o = contar(EMP), contar(ORI)
if e: D["empreendimentos"] = [{"empreendimento": n, "vendas": v} for n, v in e]
if o: D["origens"] = [{"origem": n, "vendas": v} for n, v in o]

s = s[:m.start(1)] + json.dumps(D, ensure_ascii=False) + s[m.end(1):]
s = re.sub(r'const ATUALIZADO = "[^"]*";', 'const ATUALIZADO = "%s";' % agora().strftime('%d/%m às %H:%M'), s)
s = re.sub(r'const REFRESH = "[^"]*";', 'const REFRESH = "%s";' % (sys.argv[1] if len(sys.argv[1].split('/')) > 2 else sys.argv[1].split(' ')[0] + '/' + agora().strftime('%Y') + ' ' + sys.argv[1].split(' ')[1]), s)
open(P, 'w', encoding='utf-8').write(s)
print("realizado (sem as vendas migradas):", tot if False else {k: sum(r[k] for r in D["realizado"]) for k in tot})
print("tendência:", [(t["semana"], t["ops"], t["vn"]) for t in D["tendencia"]])
print("empreendimentos:", e, "| origens:", o)
