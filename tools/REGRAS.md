# Site do time Direcional Vendas Campinas: regras e estrutura

Documento de referência para manter ou refazer do zero o site
https://direcionalvendascps.github.io/timedvcps/ (repositório GitHub `DirecionalVendasCPS/timedvcps`, branch `main`, GitHub Pages).
Última revisão: 16/11/2026.

---

## 1. Visão geral

- Site estático (HTML + CSS + JS em um arquivo por página), visual "azul-noite" com fontes Big Shoulders Display (títulos) e Figtree (texto).
- Todos os números vêm de duas planilhas Google, alimentadas pelo **Data connector for Salesforce** (refresh automático a cada 4 horas):
  - **"Contadores do mes e corujão"** (id `1GwjDiSsr6kz7A3gthsE_UYhd6jkjnV7fJ07SdAz7gtk`)
  - **"BURDIM - Gestão Semanal - GVs - CAMPINAS"** (id `1UXpwAmmcEAyXSwLAyfyN04C1A0s8N7QN8p7cc3S0cpA`)
- Os dados ficam gravados dentro de cada página (bloco `const DADOS = {...}`). Scripts Python em `tools/` leem o texto das consultas às planilhas e reescrevem esses blocos.
- **Leitura das planilhas:** pelo Claude in Chrome (login do usuário), consultas gviz no formato
  `https://docs.google.com/spreadsheets/d/<ID>/gviz/tq?tqx=out:html&gid=<GID>&tq=<consulta>` + `get_page_text`.
  Um `navigate` por `browser_batch`. O `get_page_text` descarta células vazias (colunas ambíguas pedem consultas separadas).
- **Recarga automática** (`auto-refresh.js`, atributo `data-minutos` na tag): **2 horas** em gestão, ativações, corretores, vendas, conversão e visitas; **1 hora** em agendamentos e corujão; **sem recarga** na roleta e no calendário; página inicial 10 minutos (pedido de 19/11). Antes era tudo a cada 10 minutos (`auto-refresh.js`: busca a página e os scripts de dados sem cache e recarrega mantendo a rolagem).
- **Páginas com botão "Atualizar"** mostram "Atualizado em DD/MM às HH:MM" e "Próxima atualização". O botão copia um texto (ex.: "atualizar visitas") e abre a conversa do Claude.
- **Horário das atualizações automáticas (desde 19/11 12:00):** refresh da planilha às **12:00** e a cada 4 horas (00:00, 04:00, 08:00, 12:00, 16:00, 20:00); o site atualiza **5 minutos depois**: **00:05, 04:05, 08:05, 12:05, 16:05 e 20:05** (horário de Brasília). As páginas calculam a "Próxima atualização" com `HORAS = [0,4,8,12,16,20]` e minuto `5`.

### Privacidade (regras do usuário)
- Nunca usar o token do Salesforce nem digitar credenciais.
- "base de corretores" e "base inativos" têm CPF, banco e contato: ler **só** as colunas necessárias. Publicar apenas nome, equipe/GR e **dia/mês** do aniversário (nunca o ano).
- Nunca publicar nome ou telefone de clientes.
- Histórico de credenciados publica só contagens, sem nomes.
- Não enviar mensagens no WhatsApp sem aprovação explícita. Não alterar as planilhas.

---

## 2. Planilhas, abas e colunas usadas

### Desde 17/11/2026: planilha única "Planilha Gestão CPS BURDIM - em atualização" (id `1l2j3_YLK64dBVYrdVCs0Bj_lx8hGM6Acqyb3JdPJOk0`)
Substitui as duas planilhas abaixo (as seções antigas ficam como referência).
| Aba | gid | Uso |
|---|---|---|
| Agendamentos | 344937023 | A criação, B GV, E Data, G comparecimento, H Visita Realizada, J corretor. Agendamentos criados no dia e corujão = linhas por A + J |
| Visitas | 1346363242 | I corretor, K Data |
| Pastas | 1317441261 | A criação, F corretor |
| OPs1°Sem / OPs2°Sem (nomes desde 19/11) | 2006625860 / 1837176060 | A criação, B imobiliária, C ID, Q corretor; no site é tudo "2026" (somar as duas abas) |
| Vendas | 0 | B ID, C GV, D empreendimento, E data venda, F Conf. 2.0, N Status, Q FID, S imobiliária, T corretor, AK mês da venda, AM mês da confirmação. Distratadas contam no total do mês |
| BaseAtivos (ex-Base de corretores) | 119436953 | A nome, L status, N nascimento, AI GR |
| BaseInativos (ex-Corretores inativos) | 707020357 | AA credenciamento, AD reativação, AF descredenciamento, AH motivo, AI GR, AJ GV |
- Vendas: `select B,Q,F,AK,AM` (+ blocos `B,C`, `B,T`, `B,D`) `where B is not null and (AK >= date '2026-09-01' or AM >= date '2026-09-01')`, mesmo formato do `vendas_atualizar.py`.
- Desde 18/11 existe a aba Auto Refresh Execution Log (A horário MM/DD/AAAA HH:MM:SS, linhas novas no topo; refresh a cada 4 h, ex.: 01:40, 09:40, 05:26). Aba Auxiliar_Vendas (A ID, B origem da conta, C GR). Ainda não existe: Calc_Data.
- **Sem Chrome:** dá para ler pelo conector Google Sheets (get_values), coluna por coluna; as abas vêm ordenadas da criação mais nova para a mais antiga. Nunca ler a coluna C (nome do cliente) do Agendamentos.
- Ainda não existem (o usuário vai criar): Calc_Data. Até lá a Gestão GRs/GVs fica parada, "Dados da planilha até" = horário da atualização manual e a verificação automática fica pausada.


### "Contadores do mes e corujão"
| Aba | gid | Colunas |
|---|---|---|
| agendamentos normal | 1595273579 | A data de criação, G horário agendado, H data de comparecimento, I visita realizada, K Assunto ("… - Corretor(a) NOME") |
| base de corretores | 232753372 | A nome, L status, N nascimento, AI GR (proprietário da conta) |
| base inativos | 752730205 | A nome, L status, AA Data Credenciamento, AD Data Reativação, AF Data Descredenciamento, AH Motivo, AJ GR |
| contador de vendas | 0 | A ID da oportunidade, D proprietário (GV), M empreendimento, P corretor, S FID, T Data Confirmação Venda 2.0, U mês da venda, W mês da confirmação |
| Auto Refresh Execution Log | (sheet=) | A horário do refresh, B aba |

### "BURDIM - Gestão Semanal - GVs - CAMPINAS"
| Aba | gid | Colunas |
|---|---|---|
| Oportunidades | 1177604036 | A data de criação, B imobiliária ("EQUIPE X"), C ID, Q corretor |
| Agendamentos | 885964070 | A criação, B GV, E Data (agendada), G comparecimento, H Visita Realizada (true/false), J corretor |
| Visitas | 636908934 | A código, I corretor, K Data |
| Pastas | 1699873178 | A criação, B nome da avaliação, F corretor |
| Vendas | 697354188 | A ID, D proprietário (GV), I data da venda, P corretor, Q venda comercial?, R facilitada, S FID, T mês da venda |
| Novembro/26 | (sheet=) | blocos "Meta por Gerente" e "Realizado Semanal" (por GV, semanas 01/11…06/12) |
| Calc_Data | (sheet=) | semanas (OPs AG VIS PAS VN), vendas por empreendimento e por origem |
| Auto Refresh Execution Log | (sheet=) | horário do refresh |

### Equipes
- **GRs:** Takeashi, Patricia (Paty) e Gustavo (Gustavo Moura).
- **GVs:** Aldinei, Ícaro, Pina → Takeashi · Mada (Madeleine Borges), Bruno (Bruno Miccoli), Sandro → Patricia · Ivan, Débora → Gustavo.
- **Corretor → GV:** `tools/gv.json`. Quem não está lá aparece como **"A definir"**; para achar o GV, procurar o corretor na aba Oportunidades (coluna B "EQUIPE X") ou Agendamentos (coluna B). José Carlos de Faria = GV Pina (16/11).
- **BaseAtivos (desde 19/11):** inclui os GVs; coluna **D Atividade** = "Gerente de Vendas" separa os GVs (não contam como corretores; entram só nos aniversários). Rodar `base_atualizar.py gvs.txt < base.txt`. GRs e outras pessoas fora do relatório ficam em `tools/aniversarios_extra.json` (só dia/mês).
- **Corretores ativos:** status **Ativo** ou **Reativado** na "base de corretores" (53 em 14/11/2026). Quem tem movimento mas não está ativo aparece como "fora da base".

---

## 3. Páginas (da inicial à última)

### 3.1 Página inicial (`/index.html`)
- Título "Direcional Vendas Campinas", texto "Placares do time de Campinas. Toque para abrir."
- **9 quadros, 2 por linha, centralizados** (grade de 6 colunas a partir de 780px; `.nova-linha` começa cada linha; `.sozinho` centraliza o último quando fica sozinho na linha):
  1. Agendamentos Criados no Dia · 2. Placar do Corujão
  3. Visitas do Dia · 4. Conversão Visitas x Agendamentos
  5. Contador de Vendas · 6. Calendário Black November
  7. Gestão Semanal (GRs e GVs) · 8. Gestão Semanal dos Corretores
  9. Roleta do Stand
- Botão "Ligar som" com as músicas da campanha (`audio/o-piso-e-pouco.mp3`, `audio/nos-queremos-a-meta.mp3`).

### 3.2 Agendamentos Criados no Dia (`/agendamentos/`)
- Nome antigo "Agendamentos do dia" → **"Agendamentos criados no dia"** (título da página e quadro).
- **Fonte:** "Contadores", aba **agendamentos normal**; conta **todas as linhas criadas no dia** (data de criação, coluna A), agendamentos e visitas, cujo Assunto tem "Corretor(a) NOME".
- Hero com o total do dia, "X de 53 corretores agendaram hoje", ranking de corretores e **quadros por GR → GV → corretor**.
- **Quadros das equipes e corretores em ordem alfabética** ("A definir" sempre por último).
- **Calendário** para ver dias anteriores (toque num dia).
- **"Somar dias":** botão que permite marcar 2 ou mais dias e ver a soma (ex.: sábado + domingo). Soma **só os números desta página**. O endereço guarda os dias (`#2026-11-08,2026-11-09`). Não perde a opção de ver um dia só.
- Bloco "Atualizado em / Próxima atualização" + botão Atualizar.
- Nas quintas de corujão, o placar com promessas fica na página do Corujão.
- **Script:** `tools/agend_hoje.py < linhas.txt` (consulta `select A,K where K contains 'Corretor(a)' and A >= date 'ONTEM'`). Substitui inteiros os dias que aparecem.
- **Prints:** `tools/prints_agendamentos.py PASTA` → `agend-1-placar.png`, `agend-2-ranking.png`, `agend-3-gr-<gr>.png`.

### 3.3 Placar do Corujão (`/corujao/`)
- **Corujão** = dia de agendamentos (normalmente quinta-feira, o usuário avisa). Cada corretor **promete** no grupo do WhatsApp "Time Corretores Direcional Campinas" quantos agendamentos fará.
- Placar: **feito x prometido** por corretor, GV e GR; agendamentos contados pela data de criação (aba agendamentos normal).
- `corujao/datas.js` lista as datas (do calendário Black November) e o resultado de cada um (`feito`, `prometido`, `placar`, por GR). Cada placar salvo vira `corujao/AAAA-MM-DD.html`; `corujao/` mostra o mais recente. A página do dia mostra só a data.
- **Placar do dia (desde 19/11):** `DADOS.dia`, `DADOS.ate` (só valem agendamentos marcados até essa data, regra do grupo) e `DADOS.regra` (texto mostrado no topo). Promessas em `corretores` (nome da lista do grupo) e `equipe[].lista` liga ao corretor da base. Atualizar com `tools/corujao_atualizar.py "DD/MM/AAAA HH:MM" < linhas.txt` (gviz `select A,E,J where A = date 'DIA'`). Antes de montar um corujão novo, salvar o anterior como `corujao/AAAA-MM-DD.html`.
- **Prints do corujão:** `tools/prints_corujao.py PASTA` → `corujao-1-placar.png`, `corujao-2-corretores.png`, `corujao-3-grafico.png`, `corujao-4-extras.png` (se houver), `corujao-5-gr-<gr>.png`. Pedido de 19/11: em dia de corujão, gerar os prints a cada atualização e mandar na conversa.
- `corujao/comparar.html`: compara os corujões (agendamentos em cada um, resultado por GR).
- Próxima atualização = próxima data de corujão.

### 3.4 Visitas do Dia (`/visitas/`)
- **Mesma estrutura da página de agendamentos** (hero, calendário, Somar dias, ranking, quadros por GR/GV em ordem alfabética).
- **Fonte:** "Gestão Semanal", aba **Agendamentos**:
  - **Agendamentos (vermelho)** = linhas com a **Data (coluna E)** no dia (na página o termo é "agendamentos", não "agendadas").
  - **Realizadas (verde)** = dessas, as com **Visita Realizada (coluna H) = true**.
- Por GR, GV e corretor. Calendário mostra "realizadas/agendadas" por dia (inclui dias futuros com agendadas).
- **"Somar dias"** soma **só os números desta página** (não mistura com agendamentos).
- Corretores fora da base ativa aparecem em "Fora da base de corretores" (contam no total do dia).
- **Script:** `tools/visitas_atualizar.py "DD/MM HH:MM" agendados.txt < realizadas.txt`
  - agendados: `select E,J,count(A) where E >= date '2026-10-01' group by E,J`
  - realizadas: `select E,J,count(A) where E >= date '2026-10-01' and H = 'verdadeiro' group by E,J` (a coluna H às vezes vem como booleano e às vezes como texto: testar `H = true`; se não vier nada, usar `H = 'verdadeiro'`)
- **Prints:** `tools/prints_visitas.py PASTA` → `visitas-1-placar.png`, `visitas-2-ranking.png`, `visitas-3-gr-<gr>.png`.

### 3.5 Conversão Visitas x Agendamentos (`/conversao/`)
- **Fonte (desde 16/11/2026): a mesma da página Visitas do dia** — "Gestão Semanal", aba **Agendamentos** (antes era a aba "agendamentos normal" da "Contadores", pela data de criação).
- **Agendamentos** = linhas com a **Data (coluna E)** no período.
- **Visitas** = dessas, as com **Visita Realizada (coluna H) = true**.
- **Conversão = visitas ÷ agendamentos.**
- Só entram os **dias até hoje** (agendamentos para dias que ainda não chegaram ficam de fora).
- **Rankings de corretor, GV e GR ordenados por mais visitas realizadas**; empate → maior conversão; depois nome. Barras mostram as visitas; cartões mostram as visitas em destaque e a % embaixo.
- **Topo:** botão Atualizar no canto superior direito; **linha de meses Jan…Dez** ocupando a linha toda (mês inteiro; meses sem dados apagados).
- **Calendário por dia** (igual às páginas de agendamentos e visitas): cada dia mostra visitas/agendamentos (verde/amarelo); toque num dia para ver só aquele dia; **"Somar dias"** junta 2 ou mais dias; "ver o mês" volta ao mês. O endereço guarda a escolha (`#2026-10` ou `#2026-11-14,2026-11-15`).
- **Script:** `tools/conv_atualizar.py` — roda **depois** de `visitas_atualizar.py` e lê os dados de `visitas/index.html` (`agendados`, `dias`, `equipe`, `refresh`); grava `dias` e `meses` = {corretor: [agendamentos, visitas]}.

### 3.6 Contador de Vendas (`/vendas/`)
- Título "Meta de vendas de <mês>": **"Faltam X vendas"**, "Já foram N de META vendas no mês (%)", totais **Comercial (amarelo)** e **Facilitada (azul)**.
- **Fonte:** "Contadores", aba **contador de vendas** (vendas desde 2026-09).
- **Regras das vendas:**
  1. A venda conta no **mês da confirmação (W)** quando houver; senão no **mês da venda (U)**. (`01/12/3799` em W = sem confirmação.)
  2. O placar mostra o **mês vigente**; o calendário "Consultar outros meses" mostra os demais.
  3. **Comercial** = tem **FID (S)** **ou** **Data Confirmação Venda 2.0 (T)**.
  4. **Facilitada** = **FID e T os dois em branco** (regra corrigida em 14/11/2026; antes exigia os dois para ser Comercial).
- **Metas:** `DADOS.metas["AAAA-MM"]` por GV (novembro/26: Aldinei 3, Ícaro 3, Pina 1, Mada 12, Bruno 4, Sandro 1, Ivan 5, Débora 1 = **30**), tiradas da aba Novembro/26. `metasGerais` para meses sem divisão (outubro/26: 21 comerciais, com banner da campanha). Mês sem meta mostra só o total.
- Quadros "Quanto falta para cada equipe" e "Quem já vendeu no mês".
- Venda que já está na aba **Vendas** da planilha de gestão mas ainda não chegou ao contador: pode ser incluída manualmente em `/tmp/vendas.txt` com os mesmos campos (ID, datas, GV, corretor, empreendimento). **Conferir vendas novas pela data da venda (coluna I), não pelo número da oportunidade.**
- **Script:** `tools/vendas_atualizar.py < vendas.txt` com 4 blocos `## SW` (`select A,S,T,U,W`), `## D`, `## P`, `## M`, filtro `where A is not null and (U >= date '2026-09-01' or W >= date '2026-09-01')`.

### 3.7 Calendário Black November (`/calendario/`)
- **Calendário completo de 2026** com botões de mês (Jan…Dez). **Sempre 6 semanas**, como o calendário do Windows (dias de outros meses em cinza).
- Título "Black November CPS" em novembro; nos outros meses "Calendário CPS · Mês". Endereço guarda o mês (`#2026-11`).
- Tipos de atividade: Evento Black, Evento Stand, Corujão, Divulgação, Outra atividade.
- **"+ Adicionar atividade"** e **edição das atividades já publicadas** (toque na atividade → editar data/nome/tipo ou excluir; ✎ marca as alteradas): tudo fica salvo só no navegador. **"Copiar alterações"** gera um texto com NOVA / ALTERAR / EXCLUIR para mandar ao Claude, que aplica em `ATIVIDADES` no `calendario/index.html` e publica para todos.
- **🎂 Aniversariantes** do mês selecionado: corretores ativos (só dia/mês), vindos da base de corretores (`tools/base_atualizar.py`).

### 3.8 Gestão Semanal dos GRs e GVs (`/gestao/`)
- Painel de cada GR e GV contra a meta: cartões de métrica (OPs, AG, VIS, PAS, Vendas) com realizado, meta, % do mês e % do esperado até a semana (No ritmo ≥100%, Atenção ≥70%, Abaixo), semana a semana, **funil de conversão do mês** (com premissas 50% / 33% / 40% / 25%), **Ranking dos GVs** (toque filtra) e "Últimas 6 semanas · equipe toda", vendas por empreendimento e por origem.
- Filtros por GR e GV. Texto do topo em duas linhas.
- **Canto superior direito:** botão **"Histórico de credenciados e descredenciamentos 2026 →"**, botão Atualizar e "Atualizado em / Próxima atualização".
- **Ranking dos GVs cabe no quadro sem barra de rolagem** (tabela `table-layout:fixed`; no computador o ranking fica um pouco mais largo que o funil).
- **Fonte:** "Gestão Semanal", abas **Novembro/26** (bloco "Realizado Semanal", 5 semanas: 01/11, 08/11, 15/11, 22/11, 29/11) e **Calc_Data** (tendência, empreendimentos, origens). Metas no bloco "Meta por Gerente".
- **Regra das vendas migradas:** vendas de meses anteriores lançadas em **10/11** **não contam** na semana de 08/11. Hoje: **10 da Mada e 2 do Bruno** (antes eram 11 + 2). Mesmo desconto na tendência.
- **Script:** `tools/gestao_atualizar.py "DD/MM HH:MM" mes.txt < calc.txt`. Para um novo mês: nova aba (ex.: Dezembro/26), novas semanas em `SEMANAS_ATUAL`, `MES_ATUAL` e novas metas.
- **Linha dos meses de 2026** (Jan…Dez, largura toda, abaixo do título; 6 colunas no celular): mês atual = `DADOS`; meses anteriores = `const HISTORICO` (Jul, Ago, Set e Out/26 habilitados; meses sem aba ficam apagados). Link direto: `/gestao/#2026-10`.
  - Cada mês usa a própria aba (Julho/26, Agosto/26, Setembro/26, Outubro/26) com os GVs e GRs daquele mês (ex.: Rodney com Luciano, Francisco, Vanessa, Feitosa). Semanas = semanas do cabeçalho com dias do mês; semanas finais sem números são descartadas.
  - Mês fechado: "esperado" = meta inteira do mês; textos dizem "(mês fechado)". Julho e agosto não têm vendas por semana na planilha.
  - "Últimas 6 semanas", empreendimentos e origens não mudam com o mês.
  - Script: `tools/gestao_historico.py PASTA` (um `AAAA-MM.txt` por mês, montado do get_page_text da aba). Ao virar o mês, o mês que fechou entra no HISTORICO.

### 3.9 Histórico de credenciados e descredenciamentos 2026 (`/gestao/ativacoes.html`)
- Termos: **"Credenciados"** (nunca "Ativados" ou "Contratações") e **"Descredenciados"**.
- **Fonte:** "Contadores", aba **base inativos** + base de corretores. Só contagens, sem nomes.
  - Entrada = Data Credenciamento (AA) ou, se mais recente, Data Reativação (AD).
  - Saída = Data Descredenciamento (AF), com Motivo (AH).
  - **Ativos no fim de cada mês** = ativos de hoje (53), voltando mês a mês (menos quem entrou, mais quem saiu).
- Gráfico de linha mês a mês: credenciados para cima, descredenciados para baixo, **barras do saldo com o valor (positivo ou negativo, amarelo)** e o número de ativos de cada mês.
- **Credenciados por GV e por GR (verde)**, **Motivos**, **Descredenciados por GV e por GR**.
- Nos gráficos por GV/GR **só GVs e GRs ativos**; nos demais gráficos entram todos (dinâmica ativos x inativos).
- GV de quem saiu vem da aba Oportunidades da gestão; sem oportunidade em 2026 = sem GV.
- Atualização manual (dados em `DADOS` da página).

### 3.10 Gestão Semanal dos Corretores (`/corretores/`)
- **Funil de 1 venda no mês, por corretor:** **60 OPs → 30 AG → 10 VIS → 4 PAS → 1 venda**.
- **Barra "Possibilidade de 1 venda" (0–100%)** = OPs 10% + AG 20% + VIS 30% + PAS 40%, proporcional ao quanto fez de cada etapa (máximo 100% por etapa):
  `chance = Σ peso × min(1, feito / funil)`.
- A **mesma regra vale para quem já vendeu** (não vira 100%); a venda aparece na coluna extra **"Venda no mês"**.
- Ranking ordenado por chance, depois vendas, pastas, visitas…; embaixo do nome, os números da semana atual.
- Só **corretores ativos** da base de corretores. Vendas = as mesmas do Contador de Vendas.
- Semanas do mês: a 1ª começa no dia 1, as outras em cada domingo; terminam no domingo seguinte (ou no dia 1 do mês seguinte).
- **Fonte:** "Gestão Semanal": OPs (Oportunidades, `select Q,count(C)` por semana), AG (Agendamentos, `select J,count(A)` por criação), VIS (Visitas, `select I,count(A)` por K), PAS (Pastas, `select F,count(B)`).
- **Script:** `tools/corretores_atualizar.py "DD/MM HH:MM" < semanas.txt` (blocos `## OPS|AG|VIS|PAS AAAA-MM-DD`).

### 3.11 Roleta do Stand (`/roleta/`)
- Último quadro da página inicial (sozinho na linha, centralizado). Conta **quantas vezes cada corretor esteve na roleta presencial** do stand Cores da Mata (Mangará).
- **Fonte:** fotos das folhas "Roleta" postadas no grupo do WhatsApp **GRUPO CAMPINAS GERAL** (uma folha por GR: Takeashi, Patricia, Gustavo Moura), até 15 min depois de cada roleta. Seg a sex: **8:45 e 13:45**; sáb, dom e feriados: **só 8:45**. Como o Chrome bloqueia a leitura do WhatsApp Web, o usuário manda as fotos na conversa.
- Cada nome escrito na folha = 1 presença naquela roleta (data + turno). Duas tabelas na folha: **"Equipe Squad"** e **"Corretores fora do squad"**. A parte abaixo do risco "Tarde" é a roleta das 13:45.
- **Fora do squad sem turno escrito:** decidir pela foto. Se o nome só aparece na foto da tarde, conta na tarde.
- Nomes ligados à base de corretores pelo CRECI e pelo GV (ex.: Rose = Roseli Martim Tibiriça, Teca = Teresinha Aparecida Crivelaro Lopes, Lucy = Luciane, Laionna/CRECI 301749 = Layane Bispo). **GV e GR vêm da base**, não do que está escrito na folha.
- Fotos repetidas ou versões anteriores da mesma folha contam uma vez só.
- Página: abre no **último dia com folha**; título **"Corretores no dia"** (no mês: "Corretores no mês"); quadro **% da base que veio ao stand** = corretores ativos presentes no dia ÷ corretores ativos da base (no mês, média dos dias com roleta). Número grande = **corretores diferentes que participaram** (não o número de presenças), com quantos foram de manhã e à tarde; calendário mostra corretores por dia, com **"Somar dias"** (junta 2 ou mais dias, ex.: sábado + domingo; conta corretores diferentes nos dias somados; % = média por dia; endereço `#2026-11-16,2026-11-17`); calendário por dia, resumo, ranking, **tabela "No squad" e tabela "Fora do squad"** (corretor, GV·GR, manhã, tarde, total), presenças por GR/GV (quem não foi em cinza) e "Listas registradas".
- **Fluxo pedido pelo usuário:** ele sobe as fotos das folhas na conversa → apurar os nomes, publicar na página → gerar os prints com `tools/prints_roleta.py PASTA` (`roleta-1-placar.png`, `roleta-2-squad.png`, `roleta-3-grs.png`, `roleta-4-listas.png`) e mandar para ele; ele mesmo repassa no grupo **"DV - GR Campinas"** (GRs) e no grupo **"Time Corretores Direcional Campinas"**.
- Dados em `const REGISTROS` (`{data, turno: "M"|"T", gr, squad: [...], fora: [...]}`) no `roleta/index.html`; equipe copiada da página de visitas.

### 3.12 Pasta de prints (`/prints/`)
- Imagens publicadas para abrir no Chrome e copiar (`prints/ver.html?g=<gr>` mostra um print).

---

## 4. Ordem de atualização ("atualizar tudo")
1. `base_atualizar.py < base.txt` (ativos, GR, aniversários; `select A,L,N,AI where A is not null`)
2. `agend_hoje.py < agend.txt`
3. `vendas_atualizar.py < vendas.txt`
4. `visitas_atualizar.py "DD/MM HH:MM" agendados.txt < realizadas.txt`
5. `conv_atualizar.py` (depois das visitas; usa os dados da página de visitas)
6. `corretores_atualizar.py "DD/MM HH:MM" < semanas.txt`
7. `gestao_atualizar.py "DD/MM HH:MM" mes.txt < calc.txt`
8. Conferir as páginas com o playwright (sem erros de JS), `git commit` e `git push`.

## 5. Tarefa programada
- **Desde 17/11/2026:** uma verificação encadeada (send_later, presa a esta conversa) que lê o **Auto Refresh Execution Log** da planilha nova. Achou refresh novo → "atualizar tudo" e agenda a próxima para refresh + 4h05; não achou → confere de novo em 10 min; aba do log ainda não existe → confere em 30 min; sem Chrome conectado → avisa e tenta em 30 min.
- Precisa do Chrome do usuário ligado com a extensão.

## 6. Prints para o WhatsApp
- Pedidos: **"prints das visitas"**, **"prints dos agendamentos"**, **"prints do corujão"**.
- Fluxo: atualizar os dados → gerar os prints (PNG nítido, alta qualidade) → **mostrar para o usuário validar** → depois do ok, enviar pelo **WhatsApp Web**: abrir a imagem no Chrome, **Ctrl+C**, colar com **Ctrl+V** na conversa e enviar.
- Destinos:
  - Grupo **"Time Corretores Direcional Campinas"**: prints do time (placar/total e ranking; no corujão também o gráfico).
  - No privado, cada GR o seu: **"GR Paty"** (Patricia), **"GR Takeashi"**, **"GR gustavo moura"** (Gustavo).
- Nunca enviar sem o ok do usuário.

## Linha "Dados da planilha até" (todas as páginas com botão Atualizar)
- Cada página mostra: Atualizado em (momento em que o site foi atualizado), **Dados da planilha até** (horário do último refresh da planilha, do "Auto Refresh Execution Log") e Próxima atualização.
- Rodar os scripts com `REFRESH_PLANILHA="DD/MM/AAAA HH:MM"` (agend_hoje, vendas_atualizar); visitas, corretores e gestão recebem o horário no 1º argumento. Agendamentos e Vendas usam o log da planilha "Contadores"; Visitas, Conversão (copia da página de visitas), Corretores e Gestão usam o da planilha de Gestão.
