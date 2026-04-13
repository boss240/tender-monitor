import requests, re
from datetime import datetime
def get_tenders(seen_ids=None):
    if seen_ids is None: seen_ids = set()
    print('[DREAM] Scanning...')
    results = []
    KW = ['bess','storage','battery','solar','inverter']
    try:
        r = requests.get('https://dream.gov.ua/projects?sector=energy', timeout=30, headers={'User-Agent':'Mozilla/5.0'})
        if r.status_code == 200:
            pat = r'href="(/projects/[^"]+)"[^>]*>([^<]+)'
            for path, title in re.findall(pat, r.text):
                title = title.strip()[:200]
                tid = path.replace('/projects/','').replace('/','_')
                if tid in seen_ids: continue
                tl = title.lower()
                if not any(k in tl for k in KW): continue
                results.append({'id':'DREAM-'+tid,'_raw_id':tid,'title':title,'org':'DREAM','source':'dream','platform':'dream','type':'Solar','amount':0,'currency':'UAH','deadline':'','cpvs':[],'cpv':'','status':'new','url':'https://dream.gov.ua'+path,'is_new':True,'score':65,'power_kw':0,'days_left':999,'fetched_at':datetime.utcnow().isoformat()})
                seen_ids.add(tid)
    except Exception as e: print(f'[DREAM] {e}')
    print(f'[DREAM] Found: {len(results)}')
    return results
