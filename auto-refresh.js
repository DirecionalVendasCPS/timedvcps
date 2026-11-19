// Auto-atualização das páginas do site (como portais de notícia):
// a página recarrega sozinha no intervalo do atributo data-minutos da tag <script> (padrão: 10 minutos), sempre — mesmo com a aba em segundo plano —,
// mantendo o dia/mês escolhido (#...) e a posição da tela.
// Além disso, a cada minuto confere versao.json (muda a cada publicação do site): se houve publicação nova, recarrega na hora.
// Páginas sem este script (roleta, calendário) nunca recarregam sozinhas.
(function () {
  var tag = document.currentScript || document.querySelector('script[src*="auto-refresh.js"]');
  var min = tag && +tag.getAttribute('data-minutos');
  var INTERVALO = (min > 0 ? min : 10) * 60 * 1000;
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
  // recarrega assim que uma atualização nova é publicada
  var raiz = tag ? new URL("versao.json", tag.src).href : null, versao = null;
  function confere() {
    if (!raiz) return;
    fetch(raiz + "?t=" + Date.now(), {cache: "no-store"}).then(function (r) { return r.ok ? r.json() : null; }).then(function (j) {
      if (!j || !j.v) return;
      if (versao === null) versao = j.v;
      else if (j.v !== versao) { versao = j.v; recarregar(); }
    }).catch(function () {});
  }
  confere();
  setInterval(confere, 60 * 1000);
})();
