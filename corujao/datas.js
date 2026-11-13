// Datas do corujão (do calendário Black November) e o resultado de cada um, para o calendário e a comparação.
// feito = agendamentos criados no dia (aba "agendamentos normal"); gr = agendamentos por GR [feito, prometido].
// placar = "feito/prometido" quando o placar do dia (com as promessas do grupo) foi salvo: a página fica em corujao/AAAA-MM-DD.html
// e a página principal (corujao/) mostra o corujão mais recente.
const CORUJOES = [
  {dia: "2026-11-05", rotulo: "Corujão p/ 07/11", feito: 35, corretores: 22, gr: {Takeashi: [9], Patricia: [23], Gustavo: [3]}},
  {dia: "2026-11-10", rotulo: "Corujão p/ 11/11", feito: 53, corretores: 26, gr: {Takeashi: [8], Patricia: [31], Gustavo: [14]}},
  {dia: "2026-11-12", rotulo: "Corujão p/ 14/11", feito: 60, prometido: 85, placar: "60/85", corretores: 28, cumpriram: 11, prometeram: 35,
   gr: {Takeashi: [8, 19], Patricia: [34, 42], Gustavo: [18, 24]}},
  {dia: "2026-11-19", rotulo: "Corujão p/ 21/11"},
  {dia: "2026-11-26", rotulo: "Corujão p/ 28/11"}
];
