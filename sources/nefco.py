import requests, re
from datetime import datetime
def get_tenders(seen_ids=None):
    if seen_ids is None: seen_ids = set()
    print('[NEFCO] Scanning...')
    try:
        r = requests.get('https://www.nefco.int/procurements/', timeout=30, headers={'User-Agent':'Mozilla/5.0'})
        html = r.text
    except Exception as e:
        print(f'[NEFCO] Error: {e}'); return []
    results = []
    KW = ['bess','battery','solar','pv','energy storage','ukraine','inverter']
    for m in re.finditer(r'a<[^>]+href=["\']([^"\']+procurement[^"\']*)["\'][^>]*>([^<]+)</a>', html):
        url = m.group(1)
        title = m.group(2).strip()
        if not url.startswith('http'): url = 'https://www.nefco.int' + url
        tid = re.sub(r'[^a-zA-Z0-9]','',url)[-20:]
        if tid in seen_ids: continue
        tl = title.lower()
        if not any(kwd in tl for kwd in KW): continue
        results.append({'id':'NEFCO-'+tid,'_raw_id':tid,'title':title[:200],'org':'NEFCO','source':'nefco','platform':'nefco','type':'BESS','amount':0,'currency':'EUR','deadline':'','cpvs':[],'cpv':'','status':'new','url':url,'is_new':True,'score':70,'power_kw':0,'days_left':999,'fetched_at':datetime.utcnow().isoformat()})
        seen_ids.add(tid)
    print(f'[NEFCO] Found: {len(results)}')
    return results
