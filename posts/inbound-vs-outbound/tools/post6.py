"""6 single-post variations of Inbound vs Outbound for Meher Sayyed. Writes v1..v6 .html into the build dir."""
import sys, os

B = sys.argv[1]
NAME, INIT = 'Meher Sayyed', 'MS'
SVG_BADGE = {'semrush', 'slack'}; SVG_FULL = {'canva'}
CH_ICON = {'Google Ads': 'googleads', 'Meta Ads': 'meta', 'LinkedIn Ads': 'linkedin', 'TikTok Ads': 'tiktok', 'YouTube Ads': 'youtube', 'LinkedIn': 'linkedin', 'YouTube': 'youtube'}

INB = [
    ('Search', [('Search visibility', 'Semrush', 'SEO + AEO')]),
    ('Content', [('Blog', 'PositiveSurfer', ''), ('LinkedIn', 'Canva', ''), ('YouTube', 'CapCut', ''), ('Newsletter', 'beehiiv', ''), ('Podcast', 'Riverside', '')]),
    ('Paid ads', [('Google Ads', 'Optmyzr', ''), ('Meta Ads', 'Madgicx', ''), ('LinkedIn Ads', 'Fibbler', ''), ('TikTok Ads', 'Revealbot', ''), ('YouTube Ads', 'Creatify', '')]),
    ('Relationships', [('Referrals', 'Crossbeam', ''), ('Community', 'Slack', ''), ('Webinars', 'Goldcast', ''), ('Events', 'Luma', '')]),
]
OUT = [('Cold email', 'Instantly'), ('Cold calling', 'Nooks'), ('LinkedIn DMs', 'HeyReach'), ('Gifting / direct mail', 'Sendoso'), ('Conferences / in⁠-⁠person', 'Bizzabo')]
ALL_IN = [(g, ch, tool, note) for g, rows in INB for ch, tool, note in rows]

PAL = {
    'soft': dict(bg='#F3ECE0', card='#DCCDB4', card2='#E8DDCA', ink='#2A2420', sub='#73675B', inb='#8FA58B', inbink='#2A2420', out='#C8452F', outink='#FFFFFF',
                 line='#D3C4AA', tile='#2A2420', tileink='#F3ECE0', tilesub='#B9AD9E', ring='rgba(42,36,32,.10)', accent3='#8FA58B'),
    'dark': dict(bg='#0A0A0A', card='#161616', card2='#1E1E1E', ink='#FFFFFF', sub='#9A9A9A', inb='#2BFF5B', inbink='#0A0A0A', out='#E5101A', outink='#FFFFFF',
                 line='#2A2A2A', tile='#161616', tileink='#FFFFFF', tilesub='#9A9A9A', ring='rgba(255,255,255,.14)', accent3='#FFE600'),
}

def logo(tool, s):
    k = tool.lower().replace(' ', '')
    if k in SVG_FULL: return f'<span class="lg full" style="--s:{s}px"><img src="assets/{k}.svg"></span>'
    if k in SVG_BADGE: return f'<span class="lg svg" style="--s:{s}px"><img src="assets/{k}.svg"></span>'
    return f'<span class="lg" style="--s:{s}px"><img src="assets/{k}.png"></span>'

def chicon(ch, s):
    k = CH_ICON.get(ch)
    return f'<img class="ci" style="width:{s}px;height:{s}px" src="assets/{k}.svg">' if k else ''

CSS = """
@font-face{font-family:IT;src:url(assets/intertight.ttf);font-weight:100 900}
@font-face{font-family:SI;src:url(assets/serif.ttf);font-style:italic}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1350px;overflow:hidden}
body{background:var(--bg);color:var(--ink);font-family:IT;position:relative;-webkit-font-smoothing:antialiased}
.dots{background-image:radial-gradient(circle,#1d1d1d 1.6px,transparent 1.7px);background-size:28px 28px;background-position:14px 14px}
.serif{font-family:SI;font-style:italic;font-weight:400;letter-spacing:0}
.page{position:absolute;inset:0;padding:58px 64px 0}
.tag{display:flex;align-items:center;gap:13px;font-weight:600;font-size:20px;letter-spacing:.15em;color:var(--sub);text-transform:uppercase}
.tag:before{content:'';width:15px;height:15px;background:var(--out);flex:none}
h1{font-weight:800;letter-spacing:-.035em;line-height:.95}
.hl{background:var(--out);color:var(--outink);padding:0 .1em .02em;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.foot{position:absolute;left:64px;right:64px;bottom:0;height:112px;border-top:2px solid var(--line);display:flex;align-items:center;justify-content:space-between}
.brand{display:flex;align-items:center;gap:16px;font-weight:800;font-size:29px;letter-spacing:-.015em}
.mono{width:56px;height:56px;border-radius:50%;background:var(--out);color:var(--outink);display:grid;place-items:center;font-weight:800;font-size:20px;letter-spacing:0}
.foot .r{font-weight:600;font-size:21px;color:var(--sub)}
.lg{width:var(--s);height:var(--s);border-radius:50%;flex:none;display:inline-grid;place-items:center;background:#fff;overflow:hidden;box-shadow:0 0 0 1.5px var(--ring)}
.lg img{width:100%;height:100%;display:block}
.lg.svg img{width:58%;height:58%}
.ci{flex:none;display:inline-block}
.pill{display:inline-flex;align-items:center;justify-content:center;height:44px;padding:0 20px;border-radius:22px;font-weight:800;font-size:21px;letter-spacing:.12em;flex:none}
.pin{background:var(--inb);color:var(--inbink)} .pout{background:var(--out);color:var(--outink)}
.cap{font-weight:600;font-size:15px;letter-spacing:.16em;text-transform:uppercase;color:var(--sub)}
"""

def page(pal, body, right='Save this for later ↗', dots=False):
    v = ';'.join(f'--{k}:{c}' for k, c in PAL[pal].items())
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>:root{{{v}}}{CSS}</style></head>
<body class="{'dots' if dots else ''}"><div class="page">{body}</div>
<div class="foot"><div class="brand"><div class="mono">{INIT}</div>{NAME}</div><div class="r">{right}</div></div></body></html>"""

def title(size=104):
    return f'<h1 style="font-size:{size}px">Inbound <span class="serif" style="font-size:1.08em">vs.</span> <span class="hl">Outbound.</span></h1>'

# ---------- V1: intent spectrum (dark) ----------
def v1():
    cols = [[INB[0], INB[3]], [INB[1]], [INB[2]]]
    cards = ''
    for groups in cols:
        g = ''
        for gname, rows in groups:
            g += f'<div class="gh"><i></i>{gname}</div>'
            for ch, tool, note in rows:
                g += f'<div class="r1"><div class="ch">{ch}{f"<small>{note}</small>" if note else ""}</div><div class="tl">{logo(tool, 30)}<span>{tool}</span></div></div>'
        cards += f'<div class="card">{g}</div>'
    tiles = ''.join(f'<div class="ot"><div class="n">0{i+1}</div>{logo(t, 64)}<div class="och">{c}</div><div class="otl">{t}</div></div>' for i, (c, t) in enumerate(OUT))
    body = f"""<style>
.spec{{margin-top:34px}} .spec .lab{{display:flex;justify-content:space-between;font-weight:600;font-size:21px}} .spec .lab em{{font-style:normal;color:var(--sub);letter-spacing:.16em;font-size:16px}}
.bar{{height:12px;border-radius:6px;margin-top:12px;background:linear-gradient(90deg,var(--inb) 0%,var(--inb) 33%,var(--out) 66%,var(--out) 100%)}}
.sh{{display:flex;align-items:center;gap:18px;margin-top:34px}} .sh .serif{{font-size:42px}} .sh .cnt{{margin-left:auto;color:var(--sub);font-weight:600;font-size:20px}}
.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:20px}}
.card{{background:var(--card);border-radius:24px;padding:20px 22px 12px;border:1px solid #232323}}
.gh{{display:flex;align-items:center;gap:10px;font-weight:600;font-size:15px;letter-spacing:.16em;text-transform:uppercase;color:var(--sub);margin:4px 0 6px}} .gh i{{width:10px;height:10px;background:var(--inb)}}
.r1{{padding:9px 0;border-bottom:1px solid var(--line)}} .r1:last-child{{border:0}}
.ch{{font-weight:700;font-size:22px;letter-spacing:-.01em}} .ch small{{font-weight:500;font-size:14px;color:var(--sub);margin-left:8px;letter-spacing:0}}
.tl{{display:flex;align-items:center;gap:10px;margin-top:6px;font-weight:500;font-size:18px;color:#d8d8d8}}
.gh+.r1{{}} .card .gh:not(:first-child){{margin-top:18px}}
.ots{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-top:20px}}
.ot{{background:var(--tile);border:2px solid var(--out);border-radius:22px;padding:18px 16px 18px;height:222px;display:flex;flex-direction:column;gap:10px;position:relative}}
.ot .n{{font-weight:800;font-size:30px;color:var(--out);position:absolute;right:16px;top:14px}}
.och{{font-weight:700;font-size:21px;line-height:1.12;margin-top:4px}} .otl{{font-weight:500;font-size:17px;color:var(--sub);margin-top:auto}}
</style>
<div class="tag">Go-to-market cheat sheet</div>
<div style="margin-top:22px;white-space:nowrap">{title(88)}</div>
<div class="spec"><div class="lab"><span>Already looking</span><em>BUYER INTENT</em><span>Not looking yet</span></div><div class="bar"></div></div>
<div class="sh"><span class="pill pin">INBOUND</span><span class="serif">They find you.</span><span class="cnt">15 channels</span></div>
<div class="cards">{cards}</div>
<div class="sh"><span class="pill pout">OUTBOUND</span><span class="serif">You find them.</span><span class="cnt">5 channels</span></div>
<div class="ots">{tiles}</div>"""
    return page('dark', body, dots=True)

# ---------- V2: bento board (soft) ----------
def v2():
    s_ch, s_tool, s_note = INB[0][1][0]
    content = ''.join(f'<div class="ci5">{logo(t, 62)}<b>{c}</b><span>{t}</span></div>' for c, t, n in INB[1][1])
    paid = ''.join(f'<div class="pr">{chicon(c, 28)}<b>{c}</b><em>→</em>{logo(t, 34)}<span>{t}</span></div>' for c, t, n in INB[2][1])
    rel = ''.join(f'<div class="rl">{logo(t, 52)}<div><b>{c}</b><span>{t}</span></div></div>' for c, t, n in INB[3][1])
    outs = ''.join(f'<div class="oc">{logo(t, 70)}<b>{c}</b><span>{t}</span></div>' for c, t in OUT)
    body = f"""<style>
.top{{display:flex;justify-content:space-between;align-items:flex-end;margin-top:20px}}
.sub{{font-size:30px;color:var(--sub);margin-top:14px}}
.grid{{display:grid;grid-template-columns:repeat(6,1fr);gap:18px;margin-top:40px}}
.t{{background:var(--card);border-radius:26px;padding:26px 26px;position:relative}}
.t .cap{{margin-bottom:14px;display:flex;align-items:center;gap:10px}} .t .cap:before{{content:'';width:10px;height:10px;background:var(--inb)}}
.a{{grid-column:span 2;display:flex;flex-direction:column}} .a .big{{display:flex;align-items:center;gap:16px;margin-top:auto}}
.a b{{font-weight:800;font-size:27px;line-height:1.05;letter-spacing:-.02em}} .a small{{display:block;font-weight:500;font-size:17px;color:var(--sub);margin-top:6px}}
.b{{grid-column:span 4}} .b .row{{display:flex;justify-content:space-between}}
.ci5{{display:flex;flex-direction:column;align-items:center;gap:8px;width:20%}} .ci5 b{{font-weight:700;font-size:19px;margin-top:4px}} .ci5 span{{font-weight:500;font-size:15px;color:var(--sub)}}
.c{{grid-column:span 3}} .pr{{display:flex;align-items:center;gap:12px;padding:11px 0;border-bottom:1px solid var(--line)}} .pr:last-child{{border:0}}
.pr b{{font-weight:700;font-size:20px;width:150px}} .pr em{{font-style:normal;color:var(--sub);font-size:20px;margin-right:2px}} .pr span{{font-weight:500;font-size:18px}}
.d{{grid-column:span 3;display:flex;flex-direction:column}} .stat{{margin-top:auto;display:flex;align-items:center;gap:16px;padding-top:12px}} .stat b{{font-weight:800;font-size:72px;letter-spacing:-.04em;color:var(--out);line-height:1}} .stat span{{font-family:SI;font-style:italic;font-size:26px;line-height:1.1}} .d .g{{display:grid;grid-template-columns:1fr 1fr;gap:16px 12px}} .rl{{display:flex;align-items:center;gap:14px;background:var(--card2);border-radius:18px;padding:14px}}
.rl b{{display:block;font-weight:700;font-size:20px}} .rl span{{font-weight:500;font-size:16px;color:var(--sub)}}
.e{{grid-column:span 6;background:var(--tile);color:var(--tileink)}} .e .cap{{color:var(--tilesub)}} .e .cap:before{{background:var(--out)}}
.e .row{{display:flex;justify-content:space-between;margin-top:4px}} .oc{{display:flex;flex-direction:column;align-items:center;text-align:center;gap:9px;width:19%}}
.oc b{{font-weight:700;font-size:19px;line-height:1.15;margin-top:2px}} .oc span{{font-weight:500;font-size:15px;color:var(--tilesub)}}
.sec{{display:flex;align-items:center;gap:16px;grid-column:span 6;margin-top:6px}} .sec .serif{{font-size:38px}}
</style>
<div class="tag">GTM stack · 20 channels</div>
<div style="margin-top:22px;white-space:nowrap">{title(88)}</div>
<div class="grid">
 <div class="sec"><span class="pill pin">INBOUND</span><span class="serif">They find you.</span></div>
 <div class="t a"><div class="cap">Search</div><div class="big">{logo(s_tool, 74)}<div><b>Search<br>visibility</b><small>{s_note} · {s_tool}</small></div></div></div>
 <div class="t b"><div class="cap">Content</div><div class="row">{content}</div></div>
 <div class="t c"><div class="cap">Paid ads</div>{paid}</div>
 <div class="t d"><div class="cap">Relationships</div><div class="g">{rel}</div><div class="stat"><b>15</b><span>ways buyers who are<br>already looking find you</span></div></div>
 <div class="sec"><span class="pill pout">OUTBOUND</span><span class="serif">You find them.</span></div>
 <div class="t e"><div class="row">{outs}</div></div>
</div>"""
    return page('soft', body)

# ---------- V3: pull vs push halves (dark) ----------
def v3():
    chips = ''.join(f'<div class="cp">{logo(t, 40)}<div><b>{t}</b><span>{c}</span></div></div>' for g, c, t, n in ALL_IN)
    outs = ''.join(f'<div class="oc">{logo(t, 82)}<b>{c}</b><span>{t}</span></div>' for c, t in OUT)
    body = f"""<style>
h1.pp{{font-size:150px;margin-top:18px}} .lead{{font-size:30px;color:var(--sub);margin-top:16px;line-height:1.3}} .lead b{{color:var(--ink);font-weight:700}}
.half{{border-radius:28px;padding:26px 26px 28px;margin-top:30px;background:var(--card)}}
.h1b{{border:2px solid rgba(43,255,91,.55);box-shadow:0 0 60px rgba(43,255,91,.10)}} .h2b{{border:2px solid rgba(229,16,26,.8);box-shadow:0 0 60px rgba(229,16,26,.16);margin-top:18px}}
.hd{{display:flex;align-items:center;gap:16px;margin-bottom:18px}} .hd .serif{{font-size:40px}} .hd .cnt{{margin-left:auto;color:var(--sub);font-weight:600;font-size:19px}}
.chips{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px 14px}}
.cp{{display:flex;align-items:center;gap:12px;background:var(--card2);border-radius:16px;padding:12px 12px}}
.cp b{{display:block;font-weight:700;font-size:19px;letter-spacing:-.01em}} .cp span{{display:block;font-weight:500;font-size:14px;color:var(--sub);margin-top:1px}}
.orow{{display:flex;justify-content:space-between}} .oc{{display:flex;flex-direction:column;align-items:center;text-align:center;width:19%;gap:10px}}
.oc b{{font-weight:700;font-size:20px;line-height:1.15}} .oc span{{font-weight:500;font-size:16px;color:var(--sub)}}
</style>
<div class="tag">The two ways to win customers</div>
<h1 class="pp">Pull <span class="serif" style="font-size:1.05em">vs.</span> <span class="hl">Push.</span></h1>
<div class="lead"><b>Inbound</b> pulls in people already looking. <b>Outbound</b> goes and finds the ones who aren’t.</div>
<div class="half h1b"><div class="hd"><span class="pill pin">INBOUND</span><span class="serif">They find you.</span><span class="cnt">15 channels</span></div><div class="chips">{chips}</div></div>
<div class="half h2b"><div class="hd"><span class="pill pout">OUTBOUND</span><span class="serif">You find them.</span><span class="cnt">5 channels</span></div><div class="orow">{outs}</div></div>"""
    return page('dark', body, dots=True)

# ---------- V4: logo wall (soft) ----------
def v4():
    tin = ''.join(f'<div class="w">{logo(t, 70)}<b>{t}</b><span>{c}</span></div>' for g, c, t, n in ALL_IN)
    tout = ''.join(f'<div class="w o">{logo(t, 70)}<b>{t}</b><span>{c}</span></div>' for c, t in OUT)
    body = f"""<style>
h1.wl{{font-size:118px;margin-top:20px}} .leg{{display:flex;gap:28px;margin-top:24px;font-weight:600;font-size:21px}} .leg span{{display:flex;align-items:center;gap:10px}} .leg i{{width:16px;height:16px;border-radius:50%}}
.lab{{display:flex;align-items:center;gap:14px;margin:30px 0 14px}} .lab .serif{{font-size:36px}}
.wall{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}}
.w{{background:var(--card);border-radius:22px;height:170px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:7px;text-align:center}}
.w b{{font-weight:800;font-size:19px;margin-top:6px;letter-spacing:-.01em}} .w span{{font-weight:500;font-size:14.5px;color:var(--sub);padding:0 8px;line-height:1.15}}
.w.o{{background:var(--tile);color:var(--tileink)}} .w.o span{{color:var(--tilesub)}}
</style>
<div class="tag">The GTM tool stack</div>
<h1 class="wl">20 tools.<br><span class="serif" style="font-weight:400">Two ways</span> <span class="hl">to grow.</span></h1>
<div class="leg"><span><i style="background:var(--inb)"></i>Inbound · they find you</span><span><i style="background:var(--out)"></i>Outbound · you find them</span></div>
<div class="lab"><span class="pill pin">INBOUND</span><span class="serif">for people already looking</span></div>
<div class="wall">{tin}</div>
<div class="lab"><span class="pill pout">OUTBOUND</span><span class="serif">for people who aren’t looking yet</span></div>
<div class="wall">{tout}</div>"""
    body = body.replace('height:170px', 'height:150px')
    return page('soft', body)

# ---------- V5: table (dark) ----------
def v5():
    rows = ''
    n = 1
    for g, c, t, note in ALL_IN:
        rows += f'<tr><td class="n">{n:02d}</td><td class="c">{chicon(c, 22)}<span>{c}</span><small>{g}</small></td><td><span class="ty in">IN</span></td><td class="t">{logo(t, 30)}<span>{t}</span></td></tr>'; n += 1
    for c, t in OUT:
        rows += f'<tr class="ob"><td class="n">{n:02d}</td><td class="c"><span>{c}</span><small>Outbound</small></td><td><span class="ty out">OUT</span></td><td class="t">{logo(t, 30)}<span>{t}</span></td></tr>'; n += 1
    body = f"""<style>
.hd{{display:flex;align-items:flex-end;justify-content:space-between;margin-top:18px}} h1.tb{{font-size:92px}} .hd .serif{{font-size:40px;color:var(--sub);text-align:right;line-height:1.05}}
table{{width:100%;border-collapse:collapse;margin-top:24px;background:var(--card);border-radius:22px;overflow:hidden}}
th{{text-align:left;font-weight:600;font-size:14px;letter-spacing:.16em;color:var(--sub);padding:13px 14px;border-bottom:1px solid var(--line);text-transform:uppercase}}
td{{padding:0 14px;height:44px;border-bottom:1px solid #222;font-size:19px;vertical-align:middle}} tr:last-child td{{border:0}}
td.n{{color:#5a5a5a;font-weight:700;font-size:16px;width:56px}} td.c{{font-weight:700}} td.c, td.t{{white-space:nowrap}}
td.c .ci{{vertical-align:middle;margin-right:10px}} td.c small{{font-weight:500;font-size:14px;color:var(--sub);margin-left:10px}}
td.t{{font-weight:500}} td.t .lg{{vertical-align:middle;margin-right:12px}} td.t span{{vertical-align:middle}}
.ty{{display:inline-block;font-weight:800;font-size:13px;letter-spacing:.12em;padding:5px 10px;border-radius:8px}} .ty.in{{background:rgba(43,255,91,.14);color:var(--inb)}} .ty.out{{background:var(--out);color:#fff}}
tr.ob td{{background:rgba(229,16,26,.07)}}
</style>
<div class="tag">Go-to-market · save this</div>
<div class="hd"><h1 class="tb">The GTM<br><span class="hl">stack.</span></h1><div class="serif">Inbound vs. outbound,<br>in one table.</div></div>
<table><tr><th>#</th><th>Channel</th><th>Type</th><th>Tool</th></tr>{rows}</table>"""
    return page('dark', body, dots=True)

# ---------- V6: editorial pill cloud (soft) ----------
def v6():
    pills = ''.join(f'<span class="p">{logo(t, 38)}<b>{c}</b><i>·</i><span>{t}</span></span>' for g, c, t, n in ALL_IN)
    opills = ''.join(f'<span class="p o">{logo(t, 48)}<b>{c}</b><i>·</i><span>{t}</span></span>' for c, t in OUT)
    body = f"""<style>
h1.ed{{font-size:112px;margin-top:22px;line-height:.98}} h1.ed .serif{{color:var(--out);font-weight:400}}
.lab{{display:flex;align-items:center;gap:14px;margin:34px 0 16px}} .lab .serif{{font-size:36px}}
.cloud{{display:flex;flex-wrap:wrap;gap:10px}}
.p{{display:inline-flex;align-items:center;gap:10px;background:var(--card);border-radius:30px;padding:6px 18px 6px 6px;font-size:19px}}
.p b{{font-weight:700}} .p i{{font-style:normal;color:var(--sub)}} .p span:last-child{{font-weight:500;color:var(--sub)}}
.p.o{{background:var(--tile);color:var(--tileink);font-size:23px;padding:7px 22px 7px 7px}} .p.o span:last-child{{color:var(--tilesub)}}
.close{{margin-top:32px;font-weight:800;font-size:46px;letter-spacing:-.02em}}
</style>
<div class="tag">A note on getting customers</div>
<h1 class="ed">Some buyers<br>are looking.<br><span class="serif" style="font-size:1.12em">Most aren’t.</span></h1>
<div class="lab"><span class="pill pin">INBOUND</span><span class="serif">be there when they search</span></div>
<div class="cloud">{pills}</div>
<div class="lab"><span class="pill pout">OUTBOUND</span><span class="serif">go to the rest</span></div>
<div class="cloud">{opills}</div>
<div class="close">The best teams run <span class="hl">both.</span></div>"""
    return page('soft', body)

for i, fn in enumerate([v1, v2, v3, v4, v5, v6], 1):
    open(os.path.join(B, f'v{i}.html'), 'w').write(fn())
print('html ok')
