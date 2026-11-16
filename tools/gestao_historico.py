# Grava os meses anteriores da página Gestão Semanal dos GVs (gestao/index.html → const HISTORICO).
# uso (na raiz do repo): python3 tools/gestao_historico.py PASTA
#   PASTA tem um arquivo por mês, AAAA-MM.txt, montado a partir do get_page_text da aba do mês
#   (ex.: sheet=Outubro/26) da planilha "BURDIM - Gestão Semanal - GVs - CAMPINAS":
#     SEMANAS dd/mm dd/mm ...           (as 6 datas do cabeçalho)
#     META                              (linhas do bloco "Meta por Gerente", começando pelo nome curto do GV)
#     NomeCurto GR n n n n n n [%] meta_ate meta_mes  ... (4 grupos: OPs, AG, VIS, PAS) ... vn_meta pas vis ag ops
#     REAL                              (linhas do bloco "Realizado Semanal", começando pelo nome curto do GV)
#     NomeCurto GR n n n n n n [%] tot tot ... (4 grupos) e depois 6 semanas de vendas (quando a aba tiver)
# Semanas do mês = semanas do cabeçalho que têm algum dia do mês; nos meses passados, as últimas semanas
# sem nenhum número (a aba seguinte é que traz esses dias) são descartadas.
import re, sys, json, os, datetime as dt
P = 'gestao/index.html'
GRS = ("Takeashi", "Patricia", "Gustavo", "Rodney")
NOME = {"Icaro": "Ícaro", "Debora": "Débora"}
COMPLETO = {"Aldinei": "Aldinei Rezende Fagundes", "Ícaro": "Ícaro Zivko Miranda", "Pina": "Shirley do Nascimento Pina",
            "Mada": "Madeleine Borges", "Bruno": "Bruno Miccoli de Oliveira", "Sandro": "Sandro Antonio da Silva",
            "Ivan": "Ivan de Aguiar Nascimento", "Luciano": "Luciano Calvitti Braga",
            "Francisco": "Francisco Luiz Ferreira de Figueiredo", "Mayara": "Mayara Soares Diogo",
            "Bianca": "Bianca Nascimento Sabino da Silva", "Jonatha": "Jonatha Gomes Morais de Lima",
            "Vanessa": "Vanessa de Albuquerque Sá Lobo", "Feitosa": "Emerson José Feitoza", "Walace": "Walace Martins de Jesus",
            "Leonardo": "Leonardo Divaney Alves"}
num = lambda t: re.fullmatch(r'-?\d+', t.replace('.', '')) is not None

def grupos(v):
    """4 grupos (6 semanas, % opcional, 2 totais) → listas e o resto da linha"""
    out, i = [], 0
    for _ in range(4):
        sem = [int(x) for x in v[i:i + 6]]; i += 6
        if i < len(v) and '%' in v[i]: i += 1
        tot = [int(x.replace('.', '')) for x in v[i:i + 2]]; i += 2
        out.append((sem, tot))
    return out, v[i:]

hist = {}
pasta = sys.argv[1]
for arq in sorted(os.listdir(pasta)):
    m = re.fullmatch(r'(\d{4})-(\d{2})\.txt', arq)
    if not m: continue
    ano, mes = int(m.group(1)), int(m.group(2))
    sec, semanas, metas, reais = None, [], [], []
    for l in open(os.path.join(pasta, arq), encoding='utf-8'):
        t = l.split()
        if not t: continue
        if t[0] == 'SEMANAS':
            for d in t[1:7]:
                dd, mm = map(int, d.split('/'))
                aa = ano if mm >= mes - 1 or mes == 1 else ano + 1
                if mes == 12 and mm == 1: aa = ano + 1
                if mes == 1 and mm == 12: aa = ano - 1
                semanas.append(dt.date(aa, mm, dd))
            continue
        if t[0] in ('META', 'REAL'): sec = t[0]; continue
        gi = next(i for i, x in enumerate(t) if x in GRS and i > 0)
        gv, gr = NOME.get(t[gi - 1], t[gi - 1]), t[gi]
        g, resto = grupos(t[gi + 1:])
        if sec == 'META':
            ops, ag, vis, pas = (x[1][1] for x in g)
            ints = [x.replace('.', '') for x in resto if '%' not in x]
            vn = 0
            for k in range(1, len(ints) - 3):
                if [int(y) if num(y) else None for y in ints[k:k + 4]] == [pas, vis, ag, ops]:
                    vn = int(ints[k - 1]); break
            metas.append({"gv": gv, "gr": gr, "nome": COMPLETO.get(gv, gv), "ops": ops, "ag": ag, "vis": vis, "pas": pas, "vn": vn})
        else:
            ints = []
            for x in resto:
                if num(x): ints.append(int(x))
                else: break
            vn = ints[:6] if len(ints) >= 6 else [ints[0] if ints else 0] + [0] * 5
            reais.append((gv, gr, [x[0] for x in g] + [vn]))
    # semanas do mês
    idx = [i for i, s in enumerate(semanas) if any((s + dt.timedelta(d)).month == mes for d in range(7))]
    while idx and all(sum(r[2][k][idx[-1]] for k in range(5)) == 0 for r in reais): idx.pop()
    sem_iso = [semanas[i].isoformat() for i in idx]
    real = [{"gv": gv, "gr": gr, "semana": semanas[i].isoformat(), **{k: v[j][i] for j, k in enumerate(("ops", "ag", "vis", "pas", "vn"))}}
            for gv, gr, v in reais for i in idx]
    hist[f'{ano}-{mes:02d}'] = {"semanas": sem_iso, "metas": metas, "realizado": real}
    tot = {k: sum(r[k] for r in real) for k in ("ops", "ag", "vis", "pas", "vn")}
    print(f'{ano}-{mes:02d}', len(metas), 'GVs', len(sem_iso), 'semanas', tot, '| metas:', {k: sum(x[k] for x in metas) for k in tot})

s = open(P, encoding='utf-8').read()
linha = 'const HISTORICO = ' + json.dumps(hist, ensure_ascii=False, separators=(',', ':')) + ';'
if re.search(r'^const HISTORICO = .*;$', s, re.M): s = re.sub(r'^const HISTORICO = .*;$', lambda _: linha, s, count=1, flags=re.M)
else: s = s.replace('\nconst ATUALIZADO = ', '\n' + linha + '\nconst ATUALIZADO = ', 1)
open(P, 'w', encoding='utf-8').write(s)
