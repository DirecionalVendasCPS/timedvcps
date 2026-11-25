# "Print gestão semanal GR": um print da página Gestão Semanal dos GVs para cada GR,
# do topo até a linha "Funil de conversão do mês" + "Ranking dos GVs" (rodar na raiz do repo).
# uso: python3 tools/prints_gestao_gr.py PASTA_SAIDA
# Precisa de playwright + google-chrome e das fontes em /tmp/fonts (ver prints_roleta.py).
import asyncio, sys, os
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else 'prints'
os.makedirs(OUT, exist_ok=True)
SRC = os.path.abspath('gestao/index.html')
F = "/tmp/fonts/node_modules/@fontsource"
CSS = "".join(f"@font-face{{font-family:'Big Shoulders Display';font-weight:{w};src:url(file://{F}/big-shoulders-display/files/big-shoulders-display-latin-{w}-normal.woff2)}}" for w in (600, 800, 900))
CSS += "".join(f"@font-face{{font-family:'Figtree';font-weight:{w};src:url(file://{F}/figtree/files/figtree-latin-{w}-normal.woff2)}}" for w in (400, 500, 600, 700))
async def main():
    async with async_playwright() as p:
        exe = "/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None
        b = await p.chromium.launch(executable_path=exe, args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": 1100, "height": 900}, device_scale_factor=2)
        await pg.route("https://fonts.googleapis.com/**", lambda r: r.abort())
        await pg.route("https://fonts.gstatic.com/**", lambda r: r.abort())
        await pg.goto("file://" + SRC, wait_until="load")
        await pg.add_style_tag(content=CSS)
        await pg.evaluate("document.fonts.ready")
        grs = await pg.evaluate("[...document.querySelectorAll('#f-gr option')].map(o => o.value).filter(Boolean)")
        for i, gr in enumerate(grs, 1):
            await pg.select_option('#f-gr', gr)
            await pg.wait_for_timeout(500)
            top = await pg.evaluate("document.querySelector('header').getBoundingClientRect().top + scrollY")
            bot = await pg.evaluate("document.querySelector('.grid2.fr').getBoundingClientRect().bottom + scrollY")
            await pg.screenshot(path=f"{OUT}/gestao-gr-{i}-{gr}.png", clip={"x": 0, "y": max(0, top - 16), "width": 1100, "height": bot - top + 32}, full_page=True)
            print(gr)
        await b.close()
asyncio.run(main())
