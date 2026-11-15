# funções comuns dos scripts de atualização (rodar a partir da raiz do repositório)
import os, re, unicodedata, datetime, zoneinfo
TZ = zoneinfo.ZoneInfo('America/Sao_Paulo')
agora = lambda: datetime.datetime.now(TZ)
norm = lambda s: ' '.join(unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().upper().split())
ALIAS = {"MARLI TEIXIEIRA DA COSTA": "MARLI TEIXEIRA DA COSTA", "LAYANE SILVA SANTOS BISPO SILVA SANTOS BISPO": "LAYANE SILVA SANTOS BISPO"}
def base_corretores():
    ag = open('agendamentos/index.html').read()
    return {norm(n): (n, gv, gr) for n, gv, gr in re.findall(r'\{nome: "([^"]+)", gv: "([^"]+)", gr: "([^"]+)"\}', ag)}
def nome_bonito(n, base):
    k = ALIAS.get(norm(n), norm(n))
    if k in base: return base[k][0]
    return ' '.join(w.lower() if w.lower() in ('de', 'da', 'do', 'dos', 'das') else w[:1].upper() + w[1:].lower() for w in n.split())

REFRESH_PLANILHA = os.environ.get('REFRESH_PLANILHA')  # horário do último refresh da planilha (Auto Refresh Execution Log), ex.: 15/11/2026 17:48
def grava_refresh(s):
    # atualização forçada (pedida pelo usuário): "Dados da planilha até" = agora. Rodada agendada: REFRESH_PLANILHA = horário do log da planilha.
    v = REFRESH_PLANILHA or agora().strftime('%d/%m/%Y %H:%M')
    return re.sub(r'  refresh: "[^"]*",', lambda _: f'  refresh: "{v}",', s, count=1)
