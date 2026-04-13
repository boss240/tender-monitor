import re
def detect_power(title):
    if not title: return 0
    m = re.search(r"(\d+)\s*(?:kw|kW|KW)", title, re.IGNORECASE)
    if m: return int(m.group(1))
    m = re.search(r"(\d+)\s*(?:mw|MW)", title, re.IGNORECASE)
    if m: return int(m.group(1)) * 1000
    return 0
