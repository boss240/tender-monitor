import sys
sys.path.insert(0, ".")
from sources.prozorro import get_tenders
t = get_tenders(168)
print("FOUND:", len(t))
for x in sorted(t, key=lambda x: x.get("score", 0), reverse=True)[:10]:
    print(f"  [{x.get('score',0)}] {x['title'][:70]}")