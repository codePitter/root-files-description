#!/usr/bin/env python3
"""Regenera index.html y MAPA.md desde mapa.json.
Uso: python build.py [ruta-del-proyecto]   (por defecto, la carpeta superior)
Las fechas salen de `git log` del proyecto; si no hay Git, quedan vacías."""
import json,sys,subprocess,html,datetime,pathlib
here=pathlib.Path(__file__).resolve().parent
proj=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else here.parent
root=json.load(open(here/'mapa.json',encoding='utf8'))
def dt(p):
    try: return subprocess.run(['git','-C',str(proj),'log','-1','--format=%cs','--',p.lstrip('/')],capture_output=True,text=True).stdout.strip()
    except Exception: return ''
e=html.escape
def gnames(n):return [n['p']+s+'.md' for s in n['s']]
def desc(n):
    d=n.get('d','')
    if n.get('dir') and not n['c'] and not n.get('t'): d=(d+' Contenido no listado.').strip()
    return d
def H(n,p,top=False):
    if n.get('g'):
        ds=[dt(p+'/'+f) for f in gnames(n)];m=max(ds)
        sd=n.get('sd') or ['']*len(ds)
        fs=''.join(f'<li class="f"><span class="n">{e(f)}</span><span class="d">{e(x)}</span><span class="m">{d}</span></li>' for f,x,d in zip(gnames(n),sd,ds))
        return f'<li><details><summary><span class="n">{e(n["p"])}*.md <b>×{len(n["s"])}</b></span><span class="d i">{e(n["d"])}</span><span class="m">{m}</span></summary><ul>{fs}</ul></details></li>'
    ic=' i' if n.get('i') else ''
    if n['dir']:
        if n.get('fl'):
            fl=''.join(f'<li class="f"><span class="n">{e(f)}</span><span class="m">{dt(p+"/"+f)}</span></li>' for f in n['fl'])
            return f'<li><details><summary><span class="n">{e(n["n"])}/</span><span class="d">{e(n.get("d",""))}</span></summary><ul>{fl}</ul></details></li>'
        ch=''.join(H(c,p+'/'+c.get('n','')) for c in n['c'])
        if n.get('t'): ch+='<li class="f"><span class="n">…</span><span class="d">Hay más archivos que no figuran en el tree original.</span></li>'
        return f'<li><details open><summary><span class="n">{e(n["n"])}/</span><span class="d{ic}">{e(desc(n))}</span></summary><ul>{ch}</ul></details></li>'
    return f'<li class="f"><span class="n">{e(n["n"])}</span><span class="d{ic}">{e(desc(n))}</span><span class="m">{dt(p)}</span></li>'
def M(n,p,k=0):
    s='  '*k;i='~' if n.get('i') else ''
    if n.get('g'):
        return [f'{s}- `{n["p"]}{{{",".join(n["s"])}}}.md` ×{len(n["s"])} — {i}{n["d"]} ({max(dt(p+"/"+f) for f in gnames(n))})']
    if n.get('fl'): return [f'{s}- `{n["n"]}/` — {n.get("d","")} Archivos: {", ".join(n["fl"])}']
    d=desc(n);dd=dt(p) if not n['dir'] else ''
    o=[f'{s}- `{n["n"]}{"/" if n["dir"] else ""}`'+(f' — {i}{d}' if d else '')+(f' ({dd})' if dd else '')]
    for c in n['c']: o+=M(c,p+'/'+c.get('n',''),k+1)
    if n.get('t'): o.append(f'{s}  - … (hay más archivos no listados)')
    return o
def anyk(n,k):
    return bool(n.get(k)) or any(anyk(c,k) for c in n.get('c',[]))
legend=(' `~` = descripción inferida del nombre (por confirmar).' if anyk(root,'i') else '')+(' El tree de origen estaba truncado donde dice «…».' if anyk(root,'t') else '')
legendh=legend.replace('`~`','<span style="color:var(--ac)">~</span>')
today=datetime.date.today().isoformat()
md='\n'.join([f'# {root["n"]} — mapa del proyecto',f'Generado: {today}. Fecha entre paréntesis = última modificación en Git.{legend}','']+M(root,''))+'\n'
(here/'MAPA.md').write_text(md,encoding='utf8')
page=f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{root["n"]} · mapa del proyecto</title>
<style>:root{{--bg:#f3f5f7;--ink:#1b2530;--mut:#5b6876;--line:#d6dce2;--ac:#1f6f78}}
@media(prefers-color-scheme:dark){{:root{{--bg:#12181e;--ink:#e3e8ed;--mut:#93a0ad;--line:#2a343e;--ac:#6cc3cd}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,sans-serif}}
main{{max-width:60rem;margin:0 auto;padding:1.5rem 1rem 4rem}}h1{{font-size:1.6rem;margin:0 0 .25rem;letter-spacing:-.01em}}
p{{margin:.25rem 0;color:var(--mut);font-size:.9rem;max-width:70ch}}.bar{{display:flex;gap:.5rem;flex-wrap:wrap;margin:1rem 0}}
input,button,.bar a{{font:inherit;font-size:.9rem;padding:.4rem .7rem;border:1px solid var(--line);border-radius:6px;background:transparent;color:var(--ink)}}
button,.bar a{{cursor:pointer;text-decoration:none}}button:hover,.bar a:hover{{border-color:var(--ac);color:var(--ac)}}input{{flex:1 1 12rem}}
:focus-visible{{outline:2px solid var(--ac);outline-offset:2px}}
ul{{list-style:none;margin:0;padding-left:1.1rem;border-left:1px solid var(--line)}}main>ul{{padding-left:0;border:0}}
li{{padding:.12rem 0}}summary,.f{{display:flex;gap:.2rem .9rem;flex-wrap:wrap;align-items:baseline}}summary{{cursor:pointer}}
.n{{font:.88rem ui-monospace,Consolas,monospace;font-weight:600;flex:0 0 auto}}.d{{flex:1 1 18rem;color:var(--mut);font-size:.9rem}}
.d.i{{font-style:italic}}.d.i::before{{content:"~ ";color:var(--ac)}}.m{{margin-left:auto;font:.8rem ui-monospace,monospace;color:var(--mut)}}
.n b{{color:var(--ac);font-weight:600}}</style></head><body><main>
<h1>{root["n"]}</h1><p>Mapa del proyecto, generado el {today}. Una línea por archivo y su última modificación.</p>
<p>{legendh}</p>
<div class="bar"><input id="q" type="search" placeholder="Filtrar archivos" aria-label="Filtrar archivos"><button id="cp">Copiar mapa como texto</button><a href="MAPA.md">Ver MAPA.md</a></div>
<ul>{H(root,'')}</ul></main>
<script type="text/plain" id="md">{e(md)}</script>
<script>const q=document.getElementById('q');q.oninput=()=>{{const v=q.value.toLowerCase();document.querySelectorAll('li').forEach(l=>l.hidden=v&&!l.textContent.toLowerCase().includes(v));if(v)document.querySelectorAll('details').forEach(d=>d.open=true)}};
const b=document.getElementById('cp');b.onclick=()=>navigator.clipboard.writeText(document.getElementById('md').textContent).then(()=>{{b.textContent='Copiado';setTimeout(()=>b.textContent='Copiar mapa como texto',1500)}});</script></body></html>'''
(here/'index.html').write_text(page,encoding='utf8')
print('OK',len(page),'bytes html',len(md),'bytes md')
