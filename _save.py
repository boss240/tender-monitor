import sys, json
sys.path.insert(0, ".")
from sources.prozorro import get_tenders

print("Scanning 168 hours...")
t = get_tenders(168)
print("Found:", len(t))

with open("results.json", "w", encoding="utf-8") as f:
    json.dump(t, f, ensure_ascii=False, indent=2, default=str)
print("Saved to results.json")

for x in sorted(t, key=lambda x: x.get("score", 0), reverse=True):
    print(f"  [{x.get('score',0)}] {x.get('amount',0):,.0f} UAH | {x.get('deadline','--')} | {x.get('url','')}")