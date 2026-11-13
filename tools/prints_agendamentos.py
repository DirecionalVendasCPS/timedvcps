# Gera os prints da página de agendamentos do dia (rodar na raiz do repo).
# uso: python3 tools/prints_agendamentos.py PASTA_SAIDA
# Precisa de: pip install playwright (com google-chrome no sistema) e as fontes em /tmp/fonts
#   (cd /tmp/fonts && npm i @fontsource/big-shoulders-display @fontsource/figtree)
import asyncio, sys, os
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else 'prints'
os.makedirs(OUT, exist_ok=True)
SRC = os.path.abspath('agendamentos/index.html')
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
        await pg.wait_for_timeout(500)
        top = await pg.evaluate("document.querySelector('header').getBoundingClientRect().top + scrollY")
        hb = await pg.evaluate("document.querySelector('.stats').getBoundingClientRect().bottom + scrollY")
        await pg.screenshot(path=f"{OUT}/agend-1-placar.png", clip={"x": 0, "y": max(0, top - 16), "width": 1100, "height": hb - top + 32}, full_page=True)
        await pg.locator('#grafico-sec').screenshot(path=f"{OUT}/agend-2-ranking.png")
        blocos = pg.locator('#grs > div')
        for k in range(await blocos.count()):
            nome = (await blocos.nth(k).locator('.gr-name').inner_text()).replace('GR ', '').strip().lower()
            await blocos.nth(k).screenshot(path=f'{OUT}/agend-3-gr-{nome}.png')
        await b.close()
asyncio.run(main())
