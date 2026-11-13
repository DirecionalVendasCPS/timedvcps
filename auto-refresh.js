// Auto-atualização das páginas do site (como portais de notícia):
// a cada 2 minutos confere se a página publicada mudou (nova atualização dos números)
// e, se mudou, recarrega sozinha mantendo o dia/mês escolhido (#...) e a posição da tela.
// Também confere na hora em que a aba volta a ficar visível.
(function () {
  var INTERVALO = 2 * 60 * 1000;
  var arquivos = [location.pathname];
  // scripts de dados da própria página (ex.: corujao/datas.js)
  Array.prototype.forEach.call(document.querySelectorAll("script[src]"), function (s) {
    var src = s.getAttribute("src");
    if (/^https?:|auto-refresh\.js/.test(src)) return;
    arquivos.push(new URL(src, location.href).pathname);
  });
  var base = null;
  function hash(t) { var h = 0; for (var i = 0; i < t.length; i++) h = (h * 31 + t.charCodeAt(i)) | 0; return h; }
  // primeira leitura: a versão que este navegador já tem (cache); depois: a versão publicada agora
  function ler(doCache) {
    return Promise.all(arquivos.map(function (p) {
      var req = doCache ? fetch(p, {cache: "force-cache"}) : fetch(p + "?v=" + Date.now(), {cache: "no-store"});
      return req.then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.text();
      });
    })).then(function (txts) { return txts.map(hash).join("-"); });
  }
  function conferir() {
    if (document.hidden) return;
    var p = base === null ? ler(true).then(function (h) { base = h; return ler(false); }) : ler(false);
    p.then(function (h) {
      if (h !== base) {
        try { sessionStorage.setItem("dv-scroll", String(window.scrollY)); } catch (e) {}
        location.reload();
      }
    }).catch(function () {});
  }
  try {
    var y = sessionStorage.getItem("dv-scroll");
    if (y !== null) { sessionStorage.removeItem("dv-scroll"); window.addEventListener("load", function () { window.scrollTo(0, +y); }); }
  } catch (e) {}
  if (location.protocol === "file:") return;
  conferir();
  setInterval(conferir, INTERVALO);
  document.addEventListener("visibilitychange", function () { if (!document.hidden) conferir(); });
})();
