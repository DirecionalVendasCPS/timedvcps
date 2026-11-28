// Datas do corujão (do calendário Black November) e o resultado de cada um, para o calendário e a comparação.
// feito = agendamentos criados no dia (aba "agendamentos normal"); gr = agendamentos por GR [feito, prometido].
// placar = "feito/prometido" quando o placar do dia (com as promessas do grupo) foi salvo: a página fica em corujao/AAAA-MM-DD.html
// e a página principal (corujao/) mostra o corujão mais recente.
const CORUJOES = [
  {dia: "2026-11-05", rotulo: "Corujão p/ 07/11", feito: 36, pagina: true, corretores: 23, gr: {Takeashi: [9], Patricia: [23], Gustavo: [3]}},
  {dia: "2026-11-10", rotulo: "Corujão p/ 11/11", feito: 55, pagina: true, corretores: 27, gr: {Takeashi: [8], Patricia: [32], Gustavo: [15]}},
  {dia: "2026-11-12", rotulo: "Corujão p/ 14/11", feito: 60, prometido: 85, placar: "60/85", corretores: 28, cumpriram: 11, prometeram: 35,
   gr: {Takeashi: [8, 19], Patricia: [34, 42], Gustavo: [18, 24]}},
  {dia: "2026-11-19", rotulo: "Corujão p/ 21/11", feito: 48, prometido: 71, placar: "48/71", gr: {Takeashi: [6, 11], Patricia: [37, 45], Gustavo: [5, 15]}},
  {dia: "2026-11-26", rotulo: "Corujão p/ 28/11", feito: 95, prometido: 89, placar: "95/89", gr: {Takeashi: [21, 23], Patricia: [52, 45], Gustavo: [22, 21]}},
  {dia: "2026-11-27", rotulo: "Corujinha p/ 28/11", feito: 37, prometido: 54, placar: "37/54", gr: {Takeashi: [11, 15], Patricia: [20, 28], Gustavo: [6, 11]}}
];

// corujão que está na página principal (corujao/index.html); os anteriores ficam em corujao/AAAA-MM-DD.html
const CORUJAO_ATUAL = "2026-11-27";
