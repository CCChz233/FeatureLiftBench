"""Retrieve public papers and inspect their opening figures. No experiments."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request
import subprocess
import json
import hashlib
import re

ROOT = Path(__file__).resolve().parent / 'literature_study'
ROOT.mkdir(exist_ok=True)
PAPERS = {
 'coffe_fse2025': ('https://arxiv.org/pdf/2502.02827', 4),
 'classeval_icse2024': ('https://mingwei-liu.github.io/assets/pdf/ICSE2024ClassEval-V2.pdf', 3),
 'ds1000_icml2023': ('https://proceedings.mlr.press/v202/lai23b/lai23b.pdf', 2),
 'evalplus_neurips2023': ('https://proceedings.neurips.cc/paper_files/paper/2023/file/43e9d647ccd3e4b7b5baab53f0368686-Paper-Conference.pdf', 2),
 'osworld_neurips2024': ('https://proceedings.neurips.cc/paper_files/paper/2024/file/5d413e48f84dc61244b6be550f1cd8f5-Paper-Datasets_and_Benchmarks_Track.pdf', 2),
 'swebench_iclr2024': ('https://proceedings.iclr.cc/paper_files/paper/2024/file/edac78c3e300629acfe6cbe9ca88fb84-Paper-Conference.pdf', 1),
 'repobench_iclr2024': ('https://proceedings.iclr.cc/paper_files/paper/2024/file/d191ba4c8923ed8fd8935b7c98658b5f-Paper-Conference.pdf', 2),
}
POPPLER = Path('C:/Users/CHZ/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin')

def collect(item):
    key,(url,page)=item
    try:
        target=ROOT/f'{key}.pdf'
        if not target.exists():
            opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(url,timeout=40) as response:
                data=response.read()
            if not data.startswith(b'%PDF'): raise ValueError('Not a PDF')
            target.write_bytes(data)
        txt=ROOT/f'{key}.txt'
        subprocess.run(['D:/texlive/2024/bin/windows/pdftotext.exe','-layout',str(target),str(txt)],check=True,capture_output=True)
        data=txt.read_text(encoding='utf-8')
        hits=[]
        for n,t in enumerate(data.split('\f'),1):
            m=re.search(r'(?:Figure|Fig\.)\s*1\s*[:.]',t)
            if m and n<=5: hits.append({'page':n,'caption':t[m.start():m.start()+500]})
        if hits: page=hits[0]['page']
        subprocess.run([str(POPPLER/'pdftoppm.exe'),'-f',str(page),'-l',str(page),'-scale-to','1600','-png','-singlefile',str(target),str(ROOT/f'{key}_fig1_page')],check=True,capture_output=True)
        result={'key':key,'url':url,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'figure1_page':page,'caption_hits':hits,'status':'ok'}
    except Exception as exc:
        result={'key':key,'url':url,'status':'error','error':str(exc)}
    print(json.dumps(result,ensure_ascii=True),flush=True)
    return result

if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=7) as pool:
        result=list(pool.map(collect,PAPERS.items()))
    (ROOT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
