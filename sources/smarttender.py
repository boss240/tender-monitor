import requests, re
from datetime import datetime
def get_tenders(seen_ids=None):
    if seen_ids is None: seen_ids = set()
    print('[Smart] Scanning...')
    results = []
    for term in ['inverter','accumulator','solar panel']:
        try:
            r = requests.get('https://smarttender.biz/publichnye-zakupivli-prozorro/', params={'search':term}, timeout=30, headers={'User-Agent':'Mozilla/5.0'})
            if r.status_code != 200: continue
            pat = r'href="(https?://smarttender\.biz/[^"]*UA-[^"]*)"[^>]*>\s*([^<]{10,})'
            for url, title in re.findall(pat, r.text):
                title = title.strip()[:200]
                tid = re.search(r'UA-[\d-]+', url)
                tid = tid.group() if tid else url[-20:]
                if tid in seen_ids: continue
                results.append({'id':'ST-'+tid,'_raw_id':tid,'title':title,'org':'SmartTender','source':'smarttender','platform':'smart','type':'Other','amount':0,'currency':'UAH','deadline':'','cpvs':[],'cpv':'','status':'new','url':url,'is_new':True,'score':65,'power_kw':0,'days_left':999,'fetched_at':datetime.utcnow().isoformat()})
                seen_ids.add(tid)
        except Exception as e: print(f'[Smart] {e}')
    print(f'[Smart] Found: {len(results)}')
    return results
