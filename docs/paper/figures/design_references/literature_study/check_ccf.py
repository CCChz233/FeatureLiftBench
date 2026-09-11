from pathlib import Path
import urllib.request
from html.parser import HTMLParser
import json

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.text=[]; self.links=[]
    def handle_data(self,d): self.text.append(d)
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            for k,v in attrs:
                if k=='href': self.links.append(v)

base=Path(__file__).parent
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
urls=[
 'https://www.ccf.org.cn/Academic_Evaluation/By_category/',
 'https://www.ccf.org.cn/Academic_Evaluation/AI/zgjsjxhtjgjxshy/al/',
]
records=[]
for i,url in enumerate(urls):
    try:
        with opener.open(url,timeout=20) as r: html=r.read().decode('utf-8')
        p=Page(); p.feed(html)
        text='\n'.join(t.strip() for t in p.text if t.strip())
        (base/f'ccf_official_{i}.txt').write_text(text,encoding='utf-8')
        rec={'url':url,'status':'ok','relevant_links':[l for l in p.links if any(s in l.lower() for s in ['pdf','ai/','rjgc','software'])],
             'venues':{v:text[max(0,text.find(v)-150):text.find(v)+250] for v in ['ICLR','NeurIPS','ICML','FSE','ICSE'] if v in text}}
    except Exception as e: rec={'url':url,'status':'error','error':str(e)}
    records.append(rec)
    print(json.dumps(rec,ensure_ascii=True))
(base/'ccf_check.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
