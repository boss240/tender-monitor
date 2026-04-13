import requests
from datetime import datetime
def get_tenders(seen_ids=None):
    if seen_ids is None: seen_ids = set()
    print('[TED] Scanning...')
    results = []
    for q in ['battery+storage+Ukraine','energy+storage+Ukraine','solar+Ukraine']:
        try:
            r = requests.get(f'https://ted.europa.eu/api/v3.0/notices/search?q={q}&pageSize=10&pageNum=1', timeout=30, headers={'User-Agent':'Mozilla/5.0'})
            if r.status_code != 200: continue
            for n in r.json().get('notices', r.json().get('results', [])):
                tid = str(n.get('noticeId', n.get('id','')))
                if not tid or tid in seen_ids: continue
                title = n.get('title', n.get('titleText',''))
                if isinstance(title, dict): title = title.get('en', str(title))
                results.append({'id':'TED-'+tid,'_raw_id':tid,'title':str(title)[:200],'org':'EU','source':'ted','platform':'ted','type':'BESS','amount':0,'currency':'EUR','deadline':'','cpvs':[],'cpv':'','status':'new','url':f'https://ted.europa.eu/en/notice/-/{tid}','is_new':True,'score':75,'power_kw':0,'days_left':999,'fetched_at':datetime.utcnow().isoformat()})
                seen_ids.add(tid)
        except Exception as e: print(f'[TED] {e}')
    print(f'[TED] Found: {len(results)}')
    return results
