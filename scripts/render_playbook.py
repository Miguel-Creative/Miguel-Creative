"""Build a GitHub-safe, self-contained SVG profile in the playbook's visual style.
All copy/links are read from content/profile.json. No new personal facts or metrics.
"""
from __future__ import annotations
import base64, io, json, sys, textwrap
from pathlib import Path
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from svgkit import font_face
P=json.loads((ROOT/'content/profile.json').read_text(encoding='utf-8'))
NAVY='#070b16'; PANEL='#101b2e'; BLUE='#247bff'; RED='#ff354f'
WHITE='#f3f6ff'; MUTED='#aabbd0'; LINE='#294464'

def esc(s):
    return escape(str(s), {'"':'&quot;'})

def wrap(s,n):
    return textwrap.wrap(s,n,break_long_words=False,break_on_hyphens=False) or ['']

def txt(x,y,s,size=15,color=WHITE,weight=400,extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" {extra}>{esc(s)}</text>'

def lines(x,y,s,n=58,dy=21,size=14,color=MUTED):
    return ''.join(txt(x,y+i*dy,v,size,color) for i,v in enumerate(wrap(s,n)))

def svg(k,title,w,h,body,chars=''):
    css=font_face(chars+title)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title><defs>
<linearGradient id="{k}-line" x1="0" x2="1" y1="0" y2="1"><stop stop-color="{BLUE}"/><stop offset="1" stop-color="{RED}"/></linearGradient>
<linearGradient id="{k}-shade" x1="0" x2="1" y1="1" y2="0"><stop stop-color="{NAVY}"/><stop offset="1" stop-color="#12223b"/></linearGradient>
<pattern id="{k}-dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#294464" opacity=".33"/></pattern></defs>
<style>{css}
text{{font-family:'CZ Mono',Arial,Helvetica,sans-serif}}
.float{{animation:levitate 5.5s ease-in-out infinite}}
@keyframes levitate{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-7px)}}}}
@keyframes swing{{0%,100%{{transform:rotate(-1.7deg)}}50%{{transform:rotate(1.7deg)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="22" fill="url(#{k}-shade)" stroke="{LINE}"/>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="22" fill="url(#{k}-dots)"/>
<rect x="22" width="72" height="5" rx="2" fill="{BLUE}"/><rect x="100" width="36" height="5" rx="2" fill="{RED}"/><rect x="142" width="20" height="5" rx="2" fill="{RED}" opacity=".65"/>
{body}</svg>'''

def photo_uri():
    src=ROOT/'assets/photo.png'
    if not src.exists(): return None
    from PIL import Image,ImageOps
    im=Image.open(src).convert('RGB')
    im=ImageOps.fit(im,(440,520),method=Image.Resampling.LANCZOS,centering=(.5,.38))
    b=io.BytesIO(); im.save(b,format='JPEG',quality=84,optimize=True)
    return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode('ascii')

PHOTO=photo_uri()

def portrait(x,y,w,h,clip):
    if not PHOTO:
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="#152946"/>'
    return f'<defs><clipPath id="{clip}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20"/></clipPath></defs><image href="{PHOTO}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" clip-path="url(#{clip})"/>'

def hero():
    name=P['name']; role=P['role']; founder=P['founder_of']; roles=P['typing']
    b='<rect x="35" y="47" width="535" height="262" rx="20" fill="#0d1628" stroke="#243a5c"/><rect x="44" y="58" width="9" height="9" rx="2" fill="#ff354f"/>'
    b+=txt(63,68,'PROFILE  /  '+P['login'],11,MUTED,700)
    b+=txt(53,117,'OLÁ, EU SOU',18,BLUE,700)
    b+=txt(50,192,name.upper(),70,WHITE,700,'letter-spacing="-3"')
    b+=f'<line x1="53" y1="211" x2="526" y2="211" stroke="{BLUE}" stroke-opacity=".55"/>'
    b+=txt(54,238,role,16,WHITE,700)+txt(54,262,founder,14,MUTED)
    b+='<rect x="54" y="283" width="465" height="3" rx="1.5" fill="url(#hero-line)"/>'
    for i,s in enumerate(roles):
        b+=f'<g opacity="0">{txt(54,301,s,11,BLUE)}<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.05;.23;.25;1" begin="{i*4}s" dur="{len(roles)*4}s" repeatCount="indefinite"/></g>'
    b+=f'<g class="float"><rect x="608" y="36" width="216" height="268" rx="23" fill="{PANEL}" stroke="{BLUE}" stroke-opacity=".6"/>'
    b+=portrait(619,47,194,246,'hero-face')+'</g>'
    b+=f'<rect x="578" y="269" width="256" height="42" rx="9" fill="{RED}"/>'
    b+=txt(596,295,'CREATIVE ZONE',19,WHITE,700)
    return svg('hero','Apresentação de '+name,860,342,b,name+role+founder+''.join(roles)+P['login'])

def about():
    a=P['about']; b=txt(40,61,'01   /   SOBRE MIM',23,WHITE,700)
    b+='<line x1="40" y1="76" x2="820" y2="76" stroke="url(#about-line)"/>'
    b+=txt(40,115,'QUEM SOU  /  O QUE CONSTRUO',12,BLUE,700)
    y=150
    for p in a['paragraphs']:
        b+=lines(42,y,p,58,22,14,WHITE)
        y+=len(wrap(p,58))*22+16
    b+=f'<rect x="40" y="{y+5}" width="474" height="3" rx="2" fill="{BLUE}"/>'
    b+=txt(42,y+39,P['role']+'  ·  '+P['founder_of'],12,MUTED,700)
    b+=f'<rect x="548" y="99" width="274" height="329" rx="18" fill="#111f35" stroke="{LINE}"/>'
    b+=txt(568,129,'CAPACIDADES',13,RED,700)
    for i,(k,v) in enumerate(a['facts']):
        yy=169+i*49
        b+=f'<rect x="565" y="{yy-24}" width="240" height="42" rx="9" fill="#0c172a" stroke="#243b5c"/>'
        b+=txt(575,yy-6,k.upper(),10,BLUE,700)
        b+=txt(575,yy+10,v,9.4 if len(v)>34 else 10.5,WHITE)
    return svg('about','Sobre Miguel e suas capacidades',860,480,b,' '.join(a['paragraphs'])+' '.join(k+v for k,v in a['facts'])+P['role']+P['founder_of'])

NAMES={'nodedotjs':'Node.js','githubactions':'Actions','modelcontextprotocol':'MCP','tailwindcss':'Tailwind','postgresql':'Postgres','shadcnui':'shadcn/ui','radixui':'Radix','javascript':'JavaScript','typescript':'TypeScript','cloudflare':'Cloudflare','tanstack':'TanStack'}
def tech_name(s):
    return s[5:] if s.startswith('text:') else NAMES.get(s,s.replace('dot','.').replace('css',' CSS').replace('ui',' UI').title())

def stack():
    gs=P['stack']; alltech=[tech_name(t) for _,ts in gs for t in ts]
    b=txt(38,61,'02   /   TECH STACK',23,WHITE,700)+txt(39,85,'TECNOLOGIAS, FERRAMENTAS E INFRAESTRUTURA',11,MUTED)
    b+=f'<ellipse cx="431" cy="197" rx="316" ry="70" fill="none" stroke="{BLUE}" stroke-width="2" transform="rotate(-12 431 197)" stroke-opacity=".72"/>'
    b+=f'<ellipse cx="431" cy="197" rx="240" ry="93" fill="none" stroke="{RED}" stroke-width="1.5" transform="rotate(20 431 197)" stroke-opacity=".68"/>'
    b+=f'<ellipse cx="431" cy="197" rx="156" ry="76" fill="none" stroke="{WHITE}" stroke-width="1" stroke-opacity=".28"/>'
    coords=[(154,132),(278,244),(409,126),(570,236),(706,138),(286,170),(561,172),(422,276)]
    for i,(x,y) in enumerate(coords):
        s=alltech[i]; w=max(66,len(s)*8+18)
        b+=f'<rect x="{x-w/2:.0f}" y="{y-17}" width="{w}" height="33" rx="16" fill="#11223c" stroke="{BLUE if i%2==0 else RED}" stroke-opacity=".8"/>'
        b+=txt(x,y+4,s,11,WHITE,700,'text-anchor="middle"')
    b+=txt(40,332,'STACK COMPLETA  /  ORGANIZADA POR ÁREA',12,BLUE,700)
    y=363
    for g,items in gs:
        labels=[tech_name(t) for t in items]
        b+=f'<rect x="38" y="{y-19}" width="784" height="56" rx="12" fill="#0f1c31" stroke="{LINE}"/>'
        b+=txt(51,y+2,g.upper().replace('_',' + '),11,RED,700)
        b+=txt(51,y+24,'  ·  '.join(labels),10,WHITE)
        y+=67
    return svg('stack','Tecnologias do perfil',860,max(700,y+24),b,' '.join(alltech)+' '.join(g for g,_ in gs))

def dashboard():
    name=P['name']; role=P['role']; founder=P['founder_of']
    b=txt(38,59,'03   /   IDENTIDADE DIGITAL',23,WHITE,700)
    b+=txt(39,83,'UM PERFIL REAL. DADOS REAIS. PROJETOS REAIS.',11,MUTED)
    b+=f'<line x1="250" y1="106" x2="250" y2="140" stroke="{MUTED}" stroke-width="5"/>'
    b+='<rect x="231" y="132" width="38" height="18" rx="7" fill="#8397b1" stroke="#b7c8de"/>'
    b+=f'<g style="transform-origin:250px 144px;animation:swing 5.8s ease-in-out infinite"><rect x="104" y="148" width="299" height="236" rx="17" fill="#102038" stroke="{BLUE}" stroke-width="1.5"/>'
    b+='<rect x="116" y="161" width="275" height="25" rx="7" fill="#247bff" opacity=".9"/>'
    b+=txt(134,179,'CREATIVE  /  ID',13,WHITE,700)+portrait(125,197,115,153,'id-photo')
    b+=txt(254,226,name.upper(),20,WHITE,700)+txt(254,252,'@'+P['login'],10,BLUE,700)
    b+=lines(254,276,role,19,16,10,WHITE)+lines(254,309,founder,20,16,10,MUTED)
    b+=f'<g fill="{WHITE}">'+''.join(f'<rect x="{x}" y="361" width="{2 if x%3 else 4}" height="13" opacity=".6"/>' for x in range(126,385,7))+'</g></g>'
    b+=f'<rect x="445" y="131" width="368" height="252" rx="18" fill="#0f1c31" stroke="{LINE}"/>'
    b+=txt(469,168,'DADOS DO PERFIL',16,WHITE,700)
    items=[('GITHUB','@'+P['login']),('ATUAÇÃO',role),('EMPRESA',founder),('PROJETOS',' · '.join(p['name'] for p in P['projects']))]
    for i,(k,v) in enumerate(items):
        yy=202+i*46
        b+=txt(469,yy,k,10,BLUE,700)+txt(469,yy+19,v if len(v)<49 else v[:46]+'…',10.5,WHITE)
    b+='<rect x="469" y="356" width="325" height="3" fill="url(#id-line)"/>'
    return svg('id','Identidade digital de Miguel',860,414,b,name+role+founder+' '.join(k+v for k,v in items))

def connect():
    L=P['links']
    b=txt(39,59,'04   /   VAMOS CONECTAR?',23,WHITE,700)
    b+=txt(40,82,'PROJETOS, COLABORAÇÕES E CONVERSAS',11,MUTED)
    b+=f'<rect x="38" y="111" width="228" height="234" rx="17" fill="#102038" stroke="{BLUE}"/>'
    b+=portrait(48,121,208,214,'connect-photo')
    b+=f'<path d="M262 231 H310" stroke="{RED}" stroke-width="7" stroke-linecap="round"/><path d="m297 215 17 16-17 16" stroke="{RED}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
    items=[('LINKEDIN',L['linkedin_label']),('INSTAGRAM',L['instagram_label']),('E-MAIL',L['email']),('LIVE TERMINAL','CREATIVE ZONE')]
    for i,(k,v) in enumerate(items):
        x=327+(i%2)*250; y=116+(i//2)*109
        b+=f'<rect x="{x}" y="{y}" width="239" height="98" rx="15" fill="#11213b" stroke="{BLUE if i%2==0 else RED}" stroke-opacity=".75"/>'
        b+=f'<circle cx="{x+22}" cy="{y+27}" r="8" fill="{BLUE if i%2==0 else RED}"/>'
        b+=txt(x+39,y+30,k,12,WHITE,700)+txt(x+16,y+62,v if len(v)<34 else v[:32]+'…',11,MUTED)+txt(x+213,y+78,'›',28,RED,700)
    b+=txt(40,373,'Links clicáveis disponíveis logo abaixo desta arte no README.',10,MUTED)
    return svg('connect','Conecte-se com '+P['name'],860,397,b,P['name']+' '.join(k+v for k,v in items))

def readme():
    c=P['community']; L=P['links']; cards=[]
    for i in range(0,len(P['projects']),2):
        row=['<tr>']
        for p in P['projects'][i:i+2]:
            row.append(f'<td valign="top"><a href="{esc(p["url"])}"><img src="./cards/{p["slug"]}.svg" width="420" alt="{esc(p["name"])}: {esc(p["tagline"])}"/></a></td>')
        row.append('</tr>'); cards.extend(row)
    socials=f'''[![LinkedIn](https://img.shields.io/badge/LinkedIn-{L['linkedin_label']}-247bff?style=for-the-badge&logo=linkedin&logoColor=white)]({L['linkedin']})
[![Instagram](https://img.shields.io/badge/Instagram-{L['instagram_label']}-ff354f?style=for-the-badge&logo=instagram&logoColor=white)]({L['instagram']})
[![E--mail](https://img.shields.io/badge/E--mail-Contato-247bff?style=for-the-badge&logo=gmail&logoColor=white)](mailto:{L['email']})
[![Live_Terminal](https://img.shields.io/badge/Live_Terminal-CREATIVE_ZONE-ff354f?style=for-the-badge)]({L['terminal']})'''
    return f'''<!--
 README gerado por scripts/render_static.py + scripts/render_playbook.py.
 Fonte de textos, projetos e links: content/profile.json.
 As estatísticas continuam sendo atualizadas pelo GitHub Actions.
-->
<div align="center">
<img src="./assets/hero.svg?v=1" width="860" alt="{esc(P['name'])}: {esc(P['role'])}, {esc(P['founder_of'])}" />

<img src="./assets/about-life.svg?v=1" width="860" alt="Sobre: {esc(' '.join(P['about']['paragraphs']))}" />

<details><summary>Retrato em ASCII</summary><img src="./miguel-ascii.svg" width="420" alt="Retrato em ASCII de {esc(P['name'])}" /></details>

<img src="./assets/stack.svg?v=1" width="860" alt="Tecnologias do perfil" />

<img src="./assets/id-dashboard.svg?v=1" width="860" alt="Identidade digital e informações profissionais" />

<img src="./contrib-heatmap.svg" width="860" alt="Gráfico de contribuições, atualizado diariamente" />

<img src="./stats.svg" width="860" alt="Sequência atual, maior sequência, contribuições por mês e linguagens, atualizados diariamente" />

<h3>PROJETOS EM DESTAQUE</h3>
<table>
{chr(10).join(cards)}
</table>

<h3>CREATIVE ZONE  /  COMUNIDADE</h3>
<a href="{c['forum']}"><img src="./community.svg" width="860" alt="{esc(c['name'])}: {esc(c['description'])}" /></a>

[![Fórum](https://img.shields.io/badge/Fórum-forum.creativezone.pro-ff354f?style=for-the-badge)]({c['forum']})
[![GitHub](https://img.shields.io/badge/GitHub-Creatiive--Zone-247bff?style=for-the-badge&logo=github&logoColor=white)]({c['org']})

<h3>CONTRIBUIÇÕES  /  SNAKE</h3>
<img src="./dist/snake.svg" width="860" alt="Cobrinha comendo o gráfico de contribuições" />

<img src="./assets/connect.svg?v=1" width="860" alt="Redes e contatos de {esc(P['name'])}" />

{socials}

<sub>tudo aqui é SVG gerado por código, animado sem JavaScript e atualizado todo dia pelo GitHub Actions</sub>
</div>
'''

def main():
    out=ROOT/'assets'; out.mkdir(exist_ok=True)
    things={'hero.svg':hero(),'about-life.svg':about(),'stack.svg':stack(),'id-dashboard.svg':dashboard(),'connect.svg':connect()}
    for name,s in things.items():
        (out/name).write_text(s,encoding='utf-8')
    (ROOT/'README.md').write_text(readme(),encoding='utf-8')
    print('ok: playbook layout:', ', '.join(things))

if __name__=='__main__': main()
