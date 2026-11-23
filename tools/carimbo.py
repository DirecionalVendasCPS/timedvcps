#!/usr/bin/env python3
"""Carimba o horário em todas as páginas de dados, mesmo sem dado novo.

Uso: python3 tools/carimbo.py "DD/MM/AAAA HH:MM"   (horário do último refresh da planilha)

Atualiza "Atualizado em" (agora, Brasília) e "Dados da planilha até" nas páginas
agendamentos, visitas, corretores, gestao, conversao e vendas, para ficarem iguais.
O corujão não entra: o horário dele é o dos dados do dia do corujão.
"""
import re, sys
from datetime import datetime, timezone, timedelta

if len(sys.argv) < 2 or not re.fullmatch(r"\d\d/\d\d/\d{4} \d\d:\d\d", sys.argv[1]):
    sys.exit('uso: carimbo.py "DD/MM/AAAA HH:MM"')
refresh = sys.argv[1]
agora = datetime.now(timezone(timedelta(hours=-3)))
iso = agora.strftime("%Y-%m-%dT%H:%M:00-03:00")
curto = agora.strftime("%d/%m às %H:%M")

PAGINAS = ["agendamentos", "visitas", "corretores", "conversao", "vendas"]
for p in PAGINAS:
    f = f"{p}/index.html"
    s = open(f, encoding="utf-8").read()
    s, n1 = re.subn(r'(\n\s*atualizado: )"[^"]*"', rf'\1"{iso}"', s, count=1)
    s, n2 = re.subn(r'(\n\s*refresh: )"[^"]*"', rf'\1"{refresh}"', s, count=1)
    open(f, "w", encoding="utf-8").write(s)
    print(f, "ok" if n1 and n2 else f"FALHOU ({n1},{n2})")

f = "gestao/index.html"
s = open(f, encoding="utf-8").read()
s, n1 = re.subn(r'const ATUALIZADO = "[^"]*"', f'const ATUALIZADO = "{curto}"', s, count=1)
s, n2 = re.subn(r'const REFRESH = "[^"]*"', f'const REFRESH = "{refresh}"', s, count=1)
open(f, "w", encoding="utf-8").write(s)
print(f, "ok" if n1 and n2 else f"FALHOU ({n1},{n2})")
