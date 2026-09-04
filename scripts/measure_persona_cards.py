"""Measure the rendered persona cards in real Chrome, via CDP.

jsdom reports every element as 0x0, so a jsdom assertion that the name is "in
the document" passes even when flexbox has collapsed it to zero width -- which
is the exact bug this checks for. This drives headless Chrome and reads
getBoundingClientRect, so a zero-width name is visible as a zero.
"""

import asyncio
import json
import subprocess
import sys
import urllib.request

import websockets

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/?view=store"
WANT_POOL = sys.argv[2] if len(sys.argv) > 2 else "vn-drivers"
PORT = 9333

OPEN_PICKER = """
(() => {
  const btns = [...document.querySelectorAll('button')];
  const b = btns.find(x => /matraix-persona|persona\\/datasets|pool/i.test(x.textContent || ''));
  if (!b) return 'no-picker:' + btns.slice(0,12).map(x=>(x.textContent||'').trim().slice(0,24)).join('|');
  b.click();
  return 'opened:' + (b.textContent || '').trim().slice(0, 60);
})()
"""

PICK = """
(() => {
  const want = %s;
  const nodes = [...document.querySelectorAll('button,[role="option"],li')];
  const cands = nodes.filter(x => (x.textContent || '').includes(want));
  if (!cands.length) return 'NO-OPTION | menu: ' + nodes.map(x=>(x.textContent||'').trim().slice(0,28)).filter(Boolean).slice(0,25).join(' // ');
  // Innermost match: the outer wrapper also "contains" the text but has no handler.
  const hit = cands[cands.length - 1];
  hit.click();
  return 'picked <' + hit.tagName + '> ' + (hit.textContent||'').trim().slice(0,40) + ' | candidates=' + cands.length;
})()
"""

PROBE = r"""
(() => {
  const cards = [...document.querySelectorAll('div')].filter(el => {
    const c = el.className;
    return typeof c === 'string' && /glass-tile|persona-card--selected/.test(c)
           && el.querySelector('p.font-mono') && el.querySelector('dl');
  });
  const r = el => { if (!el) return null; const b = el.getBoundingClientRect();
    return {w: Math.round(b.width), need: el.scrollWidth, clipped: el.scrollWidth > el.clientWidth + 1,
            text: (el.textContent || '').trim()}; };
  return JSON.stringify(cards.slice(0, 8).map(card => {
    const ps = card.querySelectorAll('p');
    const chip = [...card.querySelectorAll('[title]')].find(x => x.tagName !== 'DD');
    return {card: Math.round(card.getBoundingClientRect().width),
            name: r(ps[0]), code: r(ps[1]), chip: r(chip)};
  }));
})()
"""


async def main() -> int:
    proc = subprocess.Popen(
        ["/usr/bin/google-chrome", "--headless=new", f"--remote-debugging-port={PORT}",
         "--no-sandbox", "--disable-gpu", "--window-size=1600,1400",
         "--user-data-dir=/tmp/claude-1001/chrome-measure", BASE],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        page = None
        for _ in range(60):
            await asyncio.sleep(0.5)
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
                page = next(t for t in tabs if t["type"] == "page")
                break
            except Exception:
                continue
        if page is None:
            print("chrome did not expose a debugging target")
            return 1

        async with websockets.connect(page["webSocketDebuggerUrl"], max_size=None) as ws:
            counter = [0]

            async def ev(expr):
                counter[0] += 1
                mid = counter[0]
                await ws.send(json.dumps({
                    "id": mid, "method": "Runtime.evaluate",
                    "params": {"expression": expr, "returnByValue": True, "awaitPromise": True},
                }))
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get("id") == mid:
                        res = msg.get("result", {})
                        if "exceptionDetails" in res:
                            return "EXC:" + json.dumps(res["exceptionDetails"])[:200]
                        return res.get("result", {}).get("value")

            await asyncio.sleep(6)
            print("  picker:", await ev(OPEN_PICKER))
            await asyncio.sleep(1.5)
            print("  select:", await ev(PICK % json.dumps(WANT_POOL)))
            await asyncio.sleep(5)

            for _ in range(20):
                raw = await ev(PROBE)
                if isinstance(raw, str) and raw.startswith("EXC:"):
                    print(raw)
                    return 1
                cards = json.loads(raw) if raw else []
                if cards:
                    print()
                    for c in cards:
                        n, cd, ch = c["name"], c["code"], c["chip"]
                        print("  NAME {:>4}px (needs {:>4}px) {} {!r}".format(
                            n["w"], n["need"], "CLIPPED" if n["clipped"] else "fits   ", n["text"][:26]))
                    bad = [c for c in cards if c["name"]["w"] == 0 or not c["name"]["text"]]
                    clip = [c for c in cards if c["name"]["clipped"]]
                    print()
                    print("zero-width names: {}/{} | clipped names: {}/{}".format(
                        len(bad), len(cards), len(clip), len(cards)))
                    return 1 if (bad or clip) else 0
                await asyncio.sleep(1.5)
            print("no persona cards found on the page")
            return 2
    finally:
        proc.terminate()


sys.exit(asyncio.run(main()))
