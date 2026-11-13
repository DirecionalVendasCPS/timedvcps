// Auto-atualização das páginas do site (como portais de notícia):
// a cada 2 minutos a página recarrega sozinha, sempre — mesmo com a aba em segundo plano —,
// mantendo o dia/mês escolhido (#...) e a posição da tela.
(function () {
  var INTERVALO = 2 * 60 * 1000;
  var arquivos = [location.pathname];
  // scripts de dados da própria página (ex.: corujao/datas.js)
  Array.prototype.forEach.call(document.querySelectorAll("script[src]"), function (s) {
    var src = s.getAttribute("src");
    if (/^https?:|auto-refresh\.js/.test(src)) return;
    arquivos.push(new URL(src, location.href).pathname);
  });
  try {
    var y = sessionStorage.getItem("dv-scroll");
    if (y !== null) { sessionStorage.removeItem("dv-scroll"); window.addEventListener("load", function () { window.scrollTo(0, +y); }); }
  } catch (e) {}
  if (location.protocol === "file:") return;
  function recarregar() {
    try { sessionStorage.setItem("dv-scroll", String(window.scrollY)); } catch (e) {}
    // busca a versão publicada agora (atualiza o cache do navegador) e recarrega
    Promise.all(arquivos.map(function (p) { return fetch(p, {cache: "reload"}).catch(function () {}); }))
      .then(function () { location.reload(); }, function () { location.reload(); });
  }
  setInterval(recarregar, INTERVALO);
})();
