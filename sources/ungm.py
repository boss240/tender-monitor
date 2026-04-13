import requests, re
from datetime import datetime
def get_tenders(seen_ids=None):
    if seen_ids is None: seen_ids = set()
    print('[UNGM] Scanning...')
    results = []
    KW = ['solar','battery','energy storage','bess','inverter','ukraine']
    try:
        r = requests.get('https://www.ungm.org/Public/Notice', params={'keywords':'solar energy storage Ukraine'}, timeout=30, headers={'User-Agent':'Mozilla/5.0'})
        if r.status_code == 200:
            pat = r'href="(/Public/Notice/\d+)"[^>]*>\s*([^<]+)'
            for path, title in re.findall(pat, r.text):
                title = title.strip()[:200]
                tid = re.search(r'\d+', path).group()
                if tid in seen_ids: continue
                tl = title.lower()
                if not any(k in tl for k in KW): continue
                results.append({'id':'UNGM-'+tid,'_raw_id':tid,'title':title,'org':'UN','source':'ungm','platform':'ungm','type':'Solar','amount':0,'currency':'USD','deadline':'','cpvs':[],'cpv':'','status':'new','url':'https://www.ungm.org'+path,'is_new':True,'score':75,'power_kw':0,'days_left':999,'fetched_at':datetime.utcnow().isoformat()})
                seen_ids.add(tid)
    except Exception as e: print(f'[UNGM] {e}')
    print(f'[UNGM] Found: {len(results)}')
    return results
