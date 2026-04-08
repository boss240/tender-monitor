import json, re

with open("results.json", "r", encoding="utf-8") as f:
    tenders = json.load(f)

with open("uze_tender_dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

pm = {"prozorro":"prozorro","smarttender":"smart","ungm":"ungm",
      "nefco":"nefco","ted":"ted","dream":"dream","dtek":"dtek"}
tm = {"BESS":"bess","Inverter":"inverter","Solar":"solar","Other":"bess"}

dt = []
for t in tenders:
    title = t.get("title","").replace("'","\\'").replace('"','\\"')
    cpvs = t.get("cpvs", [])
    dt.append({
        "id": t.get("id",""),
        "title": title,
        "platform": pm.get(t.get("platform",t.get("source","")),"prozorro"),
        "cpv": t.get("cpv", cpvs[0] if cpvs else ""),
        "amount": t.get("amount",0),
        "deadline": t.get("deadline",""),
        "status": t.get("status","active"),
        "score": t.get("score",50),
        "type": tm.get(t.get("type",""),"bess"),
        "url": t.get("url",""),
    })

js = json.dumps(dt, ensure_ascii=False, indent=2)
match = re.search(r'const TENDERS = \[[\s\S]*?\];', html)
if match:
    html = html[:match.start()] + "const TENDERS = " + js + ";" + html[match.end():]
    print(f"[OK] {len(dt)} tenders injected")
else:
    print("[ERROR] TENDERS not found")

with open("uze_tender_dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Dashboard saved!")