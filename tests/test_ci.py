"""Corporate Design: Werte aus marke.js werden angewendet, Schriften laden offline, Logo-Platz funktioniert sicher.
Legt Bildschirmfotos (hell/dunkel) in tests/screenshots ab."""
import asyncio, re
from playwright.async_api import async_playwright
from _gemeinsam import ROOT, PROG, APP, DOCS, Pruefer
P = Pruefer("CI")
def rgb(h):
    h = h.lstrip("#"); return f"rgb({int(h[0:2],16)}, {int(h[2:4],16)}, {int(h[4:6],16)})"
async def main():
    marke = (PROG / "programm" / "marke.js").read_text(encoding="utf-8")
    prim = re.search(r'primaer:\s*"(#[0-9a-fA-F]{6})"', marke).group(1)
    text = re.search(r'text:\s*"(#[0-9a-fA-F]{6})"', marke).group(1)
    firma = re.search(r'firma:\s*"([^"]*)"', marke).group(1)
    shots = ROOT / "tests" / "screenshots"; shots.mkdir(exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": 1440, "height": 900}); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.evaluate("document.fonts.ready")
        P.check("Geist geladen", await pg.evaluate("document.fonts.check('16px Geist')"))
        P.check("Lora geladen", await pg.evaluate("document.fonts.check('600 24px Lora')"))
        P.check("Primärfarbe aus marke.js", await pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--brand').trim()") == prim)
        P.check("Akzentwort in Primärfarbe", await pg.evaluate("getComputedStyle(document.querySelector('.empty h2 em')).color") == rgb(prim))
        P.check("Aktionsknopf in Textfarbe (Website-Stil)", await pg.evaluate("getComputedStyle(document.querySelector('#pick')).backgroundColor") == rgb(text))
        P.check("Textfarbe aus marke.js", await pg.evaluate("getComputedStyle(document.body).color") == rgb(text))
        P.check("Firmenname im Kopf", firma in await pg.inner_text(".brand"))
        await pg.set_input_files("#filepick", DOCS)
        await pg.wait_for_function("state.items.length && !state.busy", timeout=240000)
        await pg.screenshot(path=str(shots / "hell.png"))
        await pg.emulate_media(color_scheme="dark"); await pg.screenshot(path=str(shots / "dunkel.png"))
        await pg.evaluate("""MARKE.logoSvg='<svg viewBox="0 0 10 10"><circle cx="5" cy="5" r="5"/><script>alert(1)</script></svg>'; applyBrand()""")
        P.check("Logo wird eingefügt", await pg.evaluate("!!document.querySelector('#logo svg circle')"))
        P.check("Skripte im Logo entfernt", await pg.evaluate("!document.querySelector('#logo script')"))
        P.check("Keine JS-Fehler", not errs, errs[:3])
        await b.close()
    P.ende()
asyncio.run(main())
