"""Datenschutz: Programm läuft ohne Netz und stellt keine einzige Anfrage ins Internet."""
import asyncio
from playwright.async_api import async_playwright
from _gemeinsam import APP, DOCS, Pruefer
P = Pruefer("Offline")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(offline=True); pg = await ctx.new_page()
        reqs = []; ctx.on("request", lambda r: reqs.append(r.url[:100]))
        await pg.goto(APP)
        await pg.set_input_files("#filepick", DOCS)
        await pg.wait_for_function("state.items.length && !state.busy", timeout=240000)
        P.check("Alle Dateien gelesen", await pg.evaluate("state.items.every(i=>i.status==='done')"))
        ext = sorted({u for u in reqs if not u.startswith(("file:", "blob:", "data:"))})
        P.check("Keine Netzanfragen", not ext, ext)
        await b.close()
    P.ende()
asyncio.run(main())
