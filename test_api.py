import sys, os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import requests
from datetime import datetime
print("="*50)
print("[TEST] Prozorro API check")
print("="*50)
print("\n[1] API connection...")
try:
    r = requests.get("https://public-api.prozorro.gov.ua/api/2.5/tenders?limit=3", timeout=15)
    r.raise_for_status()
    print(f"   [OK] API works! Got {len(r.json().get('data',[]))} tenders")
except Exception as e:
    print(f"   [FAIL] {e}"); sys.exit(1)
print("\n[2] Scanning UZE tenders (48h with pagination)...")
from sources.prozorro import get_tenders
t = get_tenders(hours_back=48, seen_ids=set())
print(f"\n   Result: {len(t)} UZE tenders found")
if t:
    print("\n   Top results:")
    for x in sorted(t, key=lambda x: x.get("score",0), reverse=True)[:10]:
        print(f"   [{x.get('score',0)}] {x['title'][:70]}...")
        print(f"       CPV: {','.join(x.get('cpvs',[]))} | UAH {x.get('amount',0):,.0f} | {x.get('deadline','---')}")
        print()
else:
    print("   (No UZE tenders in 48h. Try: python scanner.py --hours 168)")
print(f"\n{'='*50}")
print(f"[DONE] {datetime.now().strftime('%H:%M:%S')}")
