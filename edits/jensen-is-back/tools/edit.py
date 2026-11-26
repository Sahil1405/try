"""Brand edit renderer: Dark Mode palette, Inter Tight + Instrument Serif.
usage: python edit.py raw.mp4 trk_prefix words.json out.mp4 [--still t1,t2,...]
"""
import sys, os, json, math, subprocess, argparse
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fxload import fx, IT, ISI, ISR

# ---------------- brand ----------------
BLACK, PANEL, RED, WHITE, GREEN, YELLOW = (10, 10, 10), (22, 22, 22), (229, 16, 26), (255, 255, 255), (43, 255, 91), (255, 230, 0)
GREY = (150, 150, 150)
fx.RED = RED; fx.CRAYON = RED; fx.CREAMY = WHITE; fx.TAPE = YELLOW
clamp, eo, eio, eb = fx.clamp, fx.ease_out, fx.ease_inout, fx.ease_back

def _comp(c, layer, x, y, alpha=1.0, behind=False, guard=False):
    L = fx.to_np(layer) if isinstance(layer, Image.Image) else layer
    h, w = L.shape[:2]; x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(0, x), max(0, y), min(c.W, x + w), min(c.H, y + h)
    if x1 <= x0 or y1 <= y0 or alpha <= 0: return
    L = L[y0 - y:y1 - y, x0 - x:x1 - x]; a = L[..., 3:4] * alpha
    if behind: a = a * (1 - c.m[y0:y1, x0:x1, None])
    elif guard:
        yy, xx = np.ogrid[y0:y1, x0:x1]
        e = ((xx - c.fx) / (c.fw * 0.62)) ** 2 + ((yy - c.fy) / (c.fw * 0.8)) ** 2
        a = a * (1 - np.clip((1.15 - e) / 0.3, 0, 1)[..., None] * c.m[y0:y1, x0:x1, None])
    dst = c.img[y0:y1, x0:x1]; dst[:] = dst * (1 - a) + L[..., :3] * a
fx.comp = _comp
FRONT_Y = {'huge-strike': 0.655, 'crayon-write': 0.66}

_fc = {}
def F(kind, size):
    """kind: xb (ExtraBold 800), b (700), sb (600), m (500), si (serif italic), sr (serif regular)"""
    size = max(6, int(size)); k = (kind, size)
    if k not in _fc:
        if kind in ('si', 'sr'): f = ImageFont.truetype(ISI if kind == 'si' else ISR, size)
        else:
            f = ImageFont.truetype(IT, size); f.set_variation_by_axes([{'xb': 800, 'b': 700, 'sb': 600, 'm': 500, 'k': 900}[kind]])
        _fc[k] = f
    return _fc[k]

def tw(s, f): return f.getlength(s)

def text_layer(s, kind, size, fill=WHITE, shadow=0, track=0):
    f = F(kind, size); bb = f.getbbox(s); pad = int(size * 0.25 + shadow * 3)
    w = int(bb[2] - bb[0] + 2 * pad + track * len(s)); h = int(bb[3] - bb[1] + 2 * pad)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def draw(dd, col, off=(0, 0)):
        if track:
            x = pad - bb[0]
            for ch in s: dd.text((x + off[0], pad - bb[1] + off[1]), ch, font=f, fill=col); x += f.getlength(ch) + track
        else: dd.text((pad - bb[0] + off[0], pad - bb[1] + off[1]), s, font=f, fill=col)
    if shadow:
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); draw(ImageDraw.Draw(sh), (0, 0, 0, 200), (0, shadow * 0.4))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(shadow)))
        d = ImageDraw.Draw(im)
    draw(d, tuple(fill) + (255,))
    return im

def dots_bg(w, h, base=BLACK, step=26, col=(38, 38, 38)):
    im = Image.new('RGBA', (w, h), base + (255,)); d = ImageDraw.Draw(im)
    for y in range(step // 2, h, step):
        for x in range(step // 2, w, step): d.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=col + (255,))
    return im

def ctx_img(c, im, x, y, alpha=1.0, guard=False, behind=False): fx.comp(c, im, x, y, alpha, behind, guard)

PHD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'photos')
PHOTO = {  # key: (file, focal x, focal y)  focal in 0..1 of the photo
    'jensen_hook': ('Jensen_huang_stanford_2026_04_30_011.jpg', 0.6, 0.3),
    'jensen_v': ('Jensen_huang_stanford_2026_04_30_008.jpg', 0.45, 0.4),
    'jensen_12': ('Jensen_huang_stanford_2026_04_30_001.jpg', 0.55, 0.5),
    'jensen_23': ('Jensen_huang_stanford_2026_04_30_008.jpg', 0.5, 0.3),
    'trump': ('Official_Presidential_Portrait_of_President_Donald.jpg', 0.5, 0.3),
    'colette': ('Colette_Kress_1.png', 0.5, 0.35),
    'hq': ('Nvdia_Endeavor_Grand_Opening_entry.jpg', 0.5, 0.5),
    'hq2': ('NVIDIA_Headquarters.jpg', 0.5, 0.5),
    'sign': ('Nvidia_sign.jpg', 0.5, 0.5),
    'chip': ('NVidia_GK107_860_A2.jpg', 0.5, 0.5),
}
_phc = {}
def photo_np(key):
    if key not in _phc:
        f, a, b = PHOTO[key]; im = Image.open(os.path.join(PHD, f)).convert('RGB'); im.thumbnail((2400, 2400), Image.LANCZOS)
        _phc[key] = (np.asarray(im, np.float32) / 255.0, a, b)
    return _phc[key]

def cover(key, w, h, zoom=1.0, dx=0.0, dy=0.0):
    """cover-fit photo into w x h around its focal point; zoom>1 punches in (Ken Burns)."""
    a, fxp, fyp = photo_np(key); ph, pw = a.shape[:2]
    s = max(w / pw, h / ph) * zoom
    cw, ch = w / s, h / s
    cx = clamp(fxp * pw + dx * pw, cw / 2, pw - cw / 2); cy = clamp(fyp * ph + dy * ph, ch / 2, ph - ch / 2)
    M = np.float32([[s, 0, -(cx - cw / 2) * s], [0, s, -(cy - ch / 2) * s]])
    return cv2.warpAffine(a, M, (int(w), int(h)), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def photo_grade(o, dark=0.0, sat=0.8):
    lum = (o @ np.float32([0.299, 0.587, 0.114]))[..., None]
    o = lum + (o - lum) * sat; o = np.clip((o - 0.5) * 1.12 + 0.5, 0, 1)
    return o * (1 - dark)

def photo_layer(key, w, h, lt, dark=0.45, grad='left', zoom0=1.04, zoom1=1.12, dur=4.0, sat=0.75):
    o = photo_grade(cover(key, w, h, zoom0 + (zoom1 - zoom0) * clamp(lt / dur)), dark, sat)
    if grad:
        xx = np.linspace(0, 1, w, dtype=np.float32)[None, :, None]; yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
        g = np.clip(0.25 + 0.85 * (1 - xx), 0, 1) if grad == 'left' else np.zeros_like(xx)
        g = np.maximum(g, np.clip((yy - 0.55) * 2.2, 0, 1) * 0.9); o = o * (1 - g * 0.85)
    a = (np.clip(o, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(a).convert('RGBA')

def photo_card(key, w, h, r=26, border=RED, bw=6, sat=0.9):
    o = photo_grade(cover(key, w, h), 0.0, sat); im = Image.fromarray((np.clip(o, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255); im.putalpha(m)
    if bw: ImageDraw.Draw(im).rounded_rectangle([0, 0, w - 1, h - 1], r, outline=border + (255,), width=bw)
    return fx.shadowed(im, 22, 10, 160)

# full-screen photo cutaways (voice keeps running): (start, end, photo, zoom0, zoom1, label)
CUTS = [(2.28, 4.35, 'jensen_v', 1.02, 1.12)]
def cutaway(c, t):
    for s0, s1, key, z0, z1 in CUTS:
        if s0 <= t < s1:
            lt = t - s0; zin = 1 + 0.1 * (1 - eo(lt / 0.3))
            o = photo_grade(cover(key, c.W, c.H, (z0 + (z1 - z0) * clamp(lt / (s1 - s0))) * zin), 0.25, 0.8)
            c.img = o.astype(np.float32); fx.vignette(c, 0.5)
            c.m = np.zeros((c.H, c.W), np.float32); c.fx, c.fy, c.fw = c.W / 2, c.H * 0.3, c.W * 0.2
            return True
    return False

# ---------------- timeline ----------------
DUR = 49.0
SPLITS = [  # (start, end, panel builder name)
    (0.0, 2.28, 'hook'), (6.0, 10.92, 'nov12'), (18.0, 21.98, 'nov23'), (25.66, 29.86, 'confirm'), (33.25, 35.45, 'trump')]
SKILL = [
    {'fx': 'reject-stamp', 'start': 10.92, 'end': 12.2, 'text': 'DENIED', 'color': '#E5101A', 'angle': 8, 'y': 0.665},
    {'fx': 'huge-strike', 'start': 15.0, 'end': 17.98, 'text': 'comeback', 'at': 1.5},
    {'fx': 'liquid-glass-graph', 'start': 22.0, 'end': 24.4, 'text': 'NVDA stock after the vote', 'from': '0%', 'to': '30%', 'color': '#FFE600'},
    {'fx': 'spotlight', 'start': 24.4, 'end': 25.66, 'push': 1.18},
    {'fx': 'lean-in', 'start': 29.86, 'end': 31.0, 'zoom': 1.32, 'speed': 0.16},
    {'fx': 'crayon-write', 'start': 41.92, 'end': 43.6, 'text': 'Washington'},
    {'fx': 'slow-push', 'start': 44.95, 'end': 49.0, 'zoom': 1.18, 'blur': 0.004},
]
CAMFX = ('spotlight', 'lean-in', 'slow-push', 'split-headline')
# my own punch-in zoom per section: (start, end, z0, z1)
ZOOMS = [(2.28, 4.35, 1.14, 1.18), (4.35, 6.0, 1.0, 1.04), (10.92, 12.2, 1.06, 1.06), (12.2, 15.0, 1.2, 1.26),
         (15.0, 17.98, 1.0, 1.0), (21.98, 24.4, 1.12, 1.16), (31.0, 33.25, 1.1, 1.14), (35.45, 41.92, 1.0, 1.04), (41.92, 43.6, 1.0, 1.0)]

# ---------------- captions ----------------
NORMAL = {'Nvidia': 'NVIDIA', 'thirty': '30', 'cent': '%'}
EMPH = {'back!': 'red', 'quit,': 'red', 'resigns': 'red', 'spy.': 'red', 'denies': 'red', 'interim': 'green', 'CEO.': 'green',
        'no': 'red', 'plans': 'red', 'unanimously': 'green', 'reinstate': 'red', '30%': 'yellow', 'twist.': 'red', 'first.': 'green',
        'national': 'red', 'security': 'red', 'risk.': 'red', 'Trump': 'red', 'compliance': 'green', 'officer.': 'green',
        'Washington': 'red', 'infrastructure?': 'red', '11': 'yellow', 'days': 'yellow', 'officials': 'red', 'senior': 'red', 'verdict?': 'green'}

def load_words(p):
    W = json.load(open(p)); out = []
    i = 0
    while i < len(W):
        w = dict(W[i]); t = w['w']
        if t == 'thirty' and i + 2 < len(W) and W[i + 1]['w'] == 'per':
            w['w'] = '30%'; w['e'] = W[i + 2]['e']; out.append(w); i += 3; continue
        if t.lower().startswith('nvidia'): w['w'] = 'NVIDIA' + t[6:]
        out.append(w); i += 1
    # fix the one transcription where Council -> keep as spoken
    return out

def chunks(words):
    out, cur = [], []
    for k, w in enumerate(words):
        cur.append(w)
        end_p = w['w'][-1] in '.,?!'
        gap = (words[k + 1]['s'] - w['s'] > 0.55) if k + 1 < len(words) else True
        if len(cur) >= 3 or end_p or gap or sum(len(x['w']) for x in cur) > 17:
            out.append(cur); cur = []
    if cur: out.append(cur)
    res = []
    for j, ch in enumerate(out):
        s = ch[0]['s']; e = out[j + 1][0]['s'] if j + 1 < len(out) else ch[-1]['s'] + 0.7
        e = min(e, ch[-1]['s'] + 1.1)
        res.append((s, e, ch))
    return res

CAP_HIDE = [(0.0, 2.28), (24.85, 25.66), (31.0, 33.25), (43.6, 44.95), (45.7, 49.1)]
def cap_y(t):
    if any(a <= t < b for a, b in [(22.0, 24.4)]): return 0.655
    if 35.45 <= t < 41.92: return 0.862
    return 0.775

def draw_caption(c, t, CH, split_k):
    if any(a <= t < b for a, b in CAP_HIDE): return
    cur = [x for x in CH if x[0] <= t < x[1]]
    if not cur: return
    s, e, ch = cur[0]
    size = 66; gap = size * 0.28
    items = []
    for w in ch:
        txt = w['w']; style = EMPH.get(txt) or EMPH.get(txt.strip('.,?!'))
        f = F('xb' if style else 'b', size); items.append((w, txt, style, f, tw(txt, f)))
    total = sum(x[4] for x in items) + gap * (len(items) - 1)
    y = c.H * (0.905 if split_k > 0.5 else cap_y(t))
    lay = Image.new('RGBA', (c.W, int(size * 2.4)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sh = Image.new('RGBA', lay.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    x = (c.W - total) / 2; by = size * 0.55
    k_in = eb((t - s) / 0.16)
    for w, txt, style, f, wl in items:
        if t < w['s'] - 0.02: x += wl + gap; continue
        a = clamp((t - w['s'] + 0.02) / 0.08); dy = (1 - eo((t - w['s'] + 0.02) / 0.14)) * size * 0.25
        if style == 'red':
            pad = size * 0.14; kk = eo((t - w['s']) / 0.14)
            d.rounded_rectangle([x - pad, by - size * 0.08 + dy, x - pad + (wl + 2 * pad) * kk, by + size * 1.02 + dy], size * 0.12, fill=RED + (int(255 * a),))
            col = WHITE
        else: col = {'green': GREEN, 'yellow': YELLOW}.get(style, WHITE)
        ds.text((x, by + dy + 3), txt, font=f, fill=(0, 0, 0, int(230 * a)), stroke_width=3, stroke_fill=(0, 0, 0, int(200 * a)))
        d.text((x, by + dy), txt, font=f, fill=col + (int(255 * a),))
        x += wl + gap
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    out = Image.alpha_composite(sh, lay)
    sc = 0.92 + 0.08 * k_in
    if sc < 0.999: out = out.resize((int(out.width * sc), int(out.height * sc)), Image.BILINEAR)
    ctx_img(c, out, (c.W - out.width) / 2, y - out.height / 2)

# ---------------- split panels ----------------
P = 960  # panel height
SHIFT = 620

def tag(d, x, y, s, size=34, col=WHITE, sq=RED, a=255):
    d.rectangle([x, y + size * 0.18, x + size * 0.62, y + size * 0.8], fill=sq + (a,))
    xx = x + size * 1.05; f = F('sb', size)
    for ch in s: d.text((xx, y), ch, font=f, fill=col + (a,)); xx += f.getlength(ch) + size * 0.12

def line_in(lt, t0, dur=0.22): return clamp((lt - t0) / dur), (1 - eo((lt - t0) / (dur * 1.4)))

def block_word(d, x, y, s, f, size, k, a, fill=RED, txt=WHITE, pad=None):
    pad = size * 0.12 if pad is None else pad; wl = f.getlength(s); bb = f.getbbox(s)
    if k > 0: d.rectangle([x - pad, y + bb[1] - pad * 0.9, x - pad + (wl + 2 * pad) * k, y + bb[3] + pad * 0.9], fill=fill + (a,))
    d.text((x, y), s, font=f, fill=txt + (a,))
    return wl

_bg = {}
def panel_base(W, key=None, lt=0.0, dark=0.5, grad='left'):
    if key:
        im = photo_layer(key, W, P, lt, dark, grad)
        d = ImageDraw.Draw(im); d.rectangle([0, P - 7, W, P], fill=RED + (255,)); return im
    if W not in _bg:
        im = dots_bg(W, P, BLACK, 28, (30, 30, 30))
        d = ImageDraw.Draw(im); d.rectangle([0, P - 7, W, P], fill=RED + (255,))
        _bg[W] = im
    return _bg[W].copy()

def p_hook(W, lt):
    im = panel_base(W, 'jensen_hook', lt, 0.35); d = ImageDraw.Draw(im)
    tag(d, 80, 175, 'BREAKING · NVIDIA', 34)
    words = [('JENSEN', 0.0, 'xb'), ('HUANG', 0.56, 'xb'), ('is back.', 1.12, 'si')]
    y = 250
    for s, t0, kind in words:
        size = 210 if kind == 'xb' else 250
        f = F(kind, size); k = clamp((lt - t0) / 0.12)
        if k > 0:
            sc = 1.18 - 0.18 * eb((lt - t0) / 0.25)
            col = WHITE if kind == 'xb' else GREEN
            L = text_layer(s, kind, size, col, track=-6 if kind == 'xb' else 0)
            if sc != 1: L = L.resize((int(L.width * sc), int(L.height * sc)), Image.BILINEAR)
            im.alpha_composite(L, (int(80 - size * 0.25 * sc), int(y - size * 0.25 * sc + (1 - sc) * size * 0.4)))
        y += 200 if kind == 'xb' else 0
    return im

def p_nov12(W, lt):
    im = panel_base(W, 'jensen_12', lt, 0.45); d = ImageDraw.Draw(im); x0 = 80
    a0, _ = line_in(lt, 0.15); tag(d, x0, 175, 'NOVEMBER 12, 2026', 34, a=int(255 * a0))
    f1 = F('xb', 120); a, dy = line_in(lt, 0.3)
    if a > 0: d.text((x0, 250 + dy * 60), 'Jensen Huang', font=f1, fill=WHITE + (int(255 * a),))
    f2 = F('xb', 170); a, dy = line_in(lt, 1.2)
    if a > 0: block_word(d, x0 + 10, 385 + dy * 60, 'resigns.', f2, 170, eo((lt - 1.3) / 0.25), int(255 * a))
    f3 = F('m', 50); a, dy = line_in(lt, 2.2)
    if a > 0: d.text((x0, 625 + dy * 40), 'amid reports tied to a', font=f3, fill=(220, 220, 220, int(255 * a)))
    f4 = F('si', 108); a, dy = line_in(lt, 3.1)
    if a > 0:
        s = 'suspected Chinese spy'; d.text((x0, 690 + dy * 40), s, font=f4, fill=YELLOW + (int(255 * a),))
        k = eo((lt - 3.5) / 0.4); bb = f4.getbbox(s)
        if k > 0: d.rectangle([x0, 690 + bb[3] + 12, x0 + (bb[2]) * k, 690 + bb[3] + 20], fill=YELLOW + (255,))
    return im

def p_nov23(W, lt):
    im = panel_base(W, 'jensen_23', lt, 0.55); d = ImageDraw.Draw(im); x0 = 80
    a0, _ = line_in(lt, 0.15); tag(d, x0, 175, 'NOVEMBER 23, 2026 · BOARD VOTE', 34, a=int(255 * a0))
    f1 = F('xb', 118); a, dy = line_in(lt, 1.4)
    if a > 0: d.text((x0, 250 + dy * 60), 'The board votes', font=f1, fill=WHITE + (int(255 * a),))
    f2 = F('si', 190); a, dy = line_in(lt, 2.15)
    if a > 0: d.text((x0 - 6, 345 + dy * 60), 'unanimously', font=f2, fill=GREEN + (int(255 * a),))
    f3 = F('xb', 118); a, dy = line_in(lt, 2.9)
    if a > 0:
        yy = 575 + dy * 60; d.text((x0, yy), 'to ', font=f3, fill=WHITE + (int(255 * a),)); xx = x0 + f3.getlength('to ') + 12
        wl = block_word(d, xx, yy, 'reinstate', f3, 118, eo((lt - 3.08) / 0.25), int(255 * a))
        d.text((xx + wl + 22, yy), 'him.', font=f3, fill=WHITE + (int(255 * a),))
    # vote bar
    a, _ = line_in(lt, 2.15)
    if a > 0:
        by = 790; d.text((x0, by - 6), 'BOARD VOTE', font=F('sb', 30), fill=(200, 200, 200, int(255 * a)))
        k = eio((lt - 2.2) / 0.8); bx0, bx1 = x0, W - 80
        d.rounded_rectangle([bx0, by + 44, bx1, by + 72], 14, fill=(38, 38, 38, int(255 * a)))
        if k > 0: d.rounded_rectangle([bx0, by + 44, bx0 + max(28, (bx1 - bx0) * k), by + 72], 14, fill=GREEN + (int(255 * a),))
        s = f'{int(round(100 * k))}% IN FAVOUR'; f = F('xb', 34); d.text((bx1 - f.getlength(s), by - 8), s, font=f, fill=GREEN + (int(255 * a),))
    return im

def p_confirm(W, lt):
    im = panel_base(W); d = ImageDraw.Draw(im); x0 = 80
    a0, _ = line_in(lt, 0.1); tag(d, x0, 175, 'NVIDIA CONFIRMS', 34, a=int(255 * a0))
    a, _ = line_in(lt, 0.2)
    if a > 0: d.text((W - 250, 120), '“', font=F('si', 420), fill=RED + (int(255 * a),))
    f1 = F('xb', 104)
    for j, (s, t0) in enumerate([('The board took', 0.9), ('input from', 1.6)]):
        a, dy = line_in(lt, t0)
        if a > 0: d.text((x0, 255 + j * 120 + dy * 50), s, font=f1, fill=WHITE + (int(255 * a),))
    a, dy = line_in(lt, 2.25)
    if a > 0:
        yy = 500 + dy * 50; xx = x0 + 10
        wl = block_word(d, xx, yy, 'senior US officials', f1, 104, eo((lt - 2.35) / 0.35), int(255 * a))
    a, dy = line_in(lt, 3.6)
    if a > 0:
        sc = 1.25 - 0.25 * eb((lt - 3.6) / 0.3)
        L = text_layer('first.', 'si', 230, GREEN)
        L = L.resize((int(L.width * sc), int(L.height * sc)), Image.BILINEAR); L.putalpha(L.split()[3].point(lambda v: int(v * a)))
        im.alpha_composite(L, (int(x0 - 50), int(600 - (sc - 1) * 100)))
    return im

def p_trump(W, lt):
    im = panel_base(W); d = ImageDraw.Draw(im); x0 = 70
    a0, _ = line_in(lt, 0.05); tag(d, x0, 175, 'WASHINGTON', 34, a=int(255 * a0))
    a, dy = line_in(lt, 0.07)
    if a > 0: d.text((x0, 245 + dy * 50), 'Trump', font=F('xb', 170), fill=WHITE + (int(255 * a),))
    a, dy = line_in(lt, 0.63)
    if a > 0: d.text((x0, 450 + dy * 40), 'publicly', font=F('si', 140), fill=GREEN + (int(255 * a),))
    a, dy = line_in(lt, 1.11)
    if a > 0: d.text((x0, 610 + dy * 40), 'urged his', font=F('xb', 104), fill=WHITE + (int(255 * a),))
    a, dy = line_in(lt, 1.67)
    if a > 0: block_word(d, x0 + 12, 740 + dy * 40, 'return.', F('xb', 104), 104, eo((lt - 1.75) / 0.22), int(255 * a))
    return im

PANELS = {'trump': p_trump, 'hook': p_hook, 'nov12': p_nov12, 'nov23': p_nov23, 'confirm': p_confirm}

# ---------------- own overlays (face mode) ----------------
def card_bg(w, h, r=38, fill=PANEL, a=235, outline=(48, 48, 48)):
    im = Image.new('RGBA', (int(w), int(h)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, int(w) - 1, int(h) - 1], r, fill=fill + (a,), outline=outline + (255,), width=2)
    return im

def o_days(c, t):
    s, e = 2.3, 4.35; lt = t - s
    if not (s <= t < e): return
    k = eb(lt / 0.3); al = clamp((e - t) / 0.15)
    w, h = 820, 300; im = card_bg(w, h); d = ImageDraw.Draw(im)
    n = int(round(11 * eo((lt - 0.05) / 0.55)))
    d.text((40, 6), f'{n}', font=F('xb', 250), fill=YELLOW + (255,))
    d.text((360, 50), 'DAYS', font=F('xb', 120), fill=WHITE + (255,))
    d.text((364, 178), 'after he quit', font=F('si', 82), fill=(230, 230, 230, 255))
    im = fx.shadowed(im, 24, 12, 140)
    fx.place(c, im, c.W / 2, c.H * 0.655 + (1 - k) * 60, 0.85 + 0.15 * k, 0, al * clamp(lt / 0.1), guard=True)

def o_gov(c, t):
    s, e = 4.36, 6.0; lt = t - s
    if not (s <= t < e): return
    k = eb(lt / 0.3); al = clamp((e - t) / 0.12)
    f = F('xb', 96); s1 = 'US GOVERNMENT'; w = int(f.getlength(s1) + 70)
    im = Image.new('RGBA', (w + 40, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    kk = eo((lt - 0.05) / 0.25); d.rectangle([20, 20, 20 + w * kk, 150], fill=RED + (255,))
    d.text((55, 30), s1, font=f, fill=WHITE + (255,))
    a2 = clamp((lt - 0.75) / 0.15); d.text((60, 160), 'weighed in.', font=F('si', 110), fill=(255, 255, 255, int(255 * a2)))
    im = fx.shadowed(im, 20, 10, 150)
    fx.place(c, im, c.W / 2, c.H * 0.66 + (1 - k) * 50, 0.9 + 0.1 * k, 2, al * clamp(lt / 0.08), guard=True)

_cache = {}
def o_chyron(c, t):
    s, e = 12.24, 14.98; lt = t - s
    if not (s <= t < e): return
    al = clamp((e - t) / 0.18); x0 = 64; y0 = c.H * 0.6
    lay = Image.new('RGBA', (c.W, 400), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    k1 = eo(lt / 0.25); f1 = F('xb', 40); s1 = 'INTERIM CEO'; w1 = f1.getlength(s1) + 44
    d.rectangle([0, 0, w1 * k1, 66], fill=RED + (255,))
    if k1 > 0.6: d.text((22, 9), s1, font=f1, fill=WHITE + (255,))
    k2 = eo((lt - 0.12) / 0.32); f2 = F('xb', 92); s2 = 'Colette Kress'; w2 = f2.getlength(s2) + 70
    d.rectangle([0, 72, w2 * k2, 72 + 128], fill=WHITE + (255,))
    if k2 > 0.5:
        lay2 = Image.new('RGBA', lay.size, (0, 0, 0, 0)); ImageDraw.Draw(lay2).text((34, 82), s2, font=f2, fill=BLACK + (255,))
        m = Image.new('L', lay.size, 0); ImageDraw.Draw(m).rectangle([0, 72, w2 * k2, 200], fill=255)
        lay.paste(lay2, (0, 0), Image.composite(lay2.split()[3], Image.new('L', lay.size, 0), m))
    k3 = clamp((lt - 1.4) / 0.2)
    if k3 > 0: d.text((4, 214), 'takes over · NVIDIA', font=F('sb', 40), fill=(235, 235, 235, int(255 * k3)))
    lay = fx.shadowed(lay, 16, 8, 120)
    ctx_img(c, lay, x0 - 32, y0 - 32, al, guard=True)
    kp = eb((lt - 0.2) / 0.3)
    if kp > 0:
        pc = _cache.setdefault('colette', photo_card('colette', 250, 310, 24, RED, 6))
        fx.place(c, pc, c.W - 175, y0 + 120, 0.7 + 0.3 * kp, -4, al * clamp((lt - 0.2) / 0.1), guard=True)

def o_tape(c, t):
    s, e = 31.0, 33.25; lt = t - s
    if not (s <= t < e): return
    al = clamp((e - t) / 0.18)
    for j, (txt, t0, rot, yy) in enumerate([('NO NATIONAL', 0.08, 3.0, 0.635), ('SECURITY RISK.', 0.85, -2.5, 0.715)]):
        k = clamp((lt - t0) / 0.1)
        if k <= 0: continue
        f = F('xb', 92); w = int(f.getlength(txt) + 80); h = 140
        im = Image.new('RGBA', (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle([12, 12, w + 11, h + 11], fill=(0, 0, 0, 255)); d.rectangle([0, 0, w - 1, h - 1], fill=YELLOW + (255,))
        for zx in range(0, w, 14): d.polygon([(zx, 0), (zx + 7, 6), (zx + 14, 0)], fill=(0, 0, 0, 0)); d.polygon([(zx, h - 1), (zx + 7, h - 7), (zx + 14, h - 1)], fill=(0, 0, 0, 0))
        d.text((40, 16), txt, font=f, fill=BLACK + (255,))
        sc = 1.35 - 0.35 * eo((lt - t0) / 0.12)
        fx.place(c, im, c.W / 2 + (j * 2 - 1) * 18, c.H * yy, sc, rot, al * k, guard=True)

CHK = [('Hire a chief compliance officer', 'NEW ROLE', 36.2, 37.5), ('Add a National Security Council', 'ADDED', 37.96, 39.9),
       ('Cooperate with investigations', 'ONGOING', 40.04, 41.35)]
def o_checklist(c, t):
    s, e = 35.45, 41.92; lt = t - s
    if not (s <= t < e): return
    al = clamp((e - t) / 0.2) * clamp(lt / 0.12); q = eo(lt / 0.35)
    W = c.W; cw, rh, hh = int(W * 0.9), 108, 124; chh = hh + rh * 3 + 30
    im = card_bg(cw, chh, 40, PANEL, 240); d = ImageDraw.Draw(im)
    d.rectangle([40, hh / 2 - 14, 68, hh / 2 + 14], fill=RED + (255,))
    d.text((88, hh / 2), "NVIDIA's next moves", font=F('xb', 46), fill=WHITE + (255,), anchor='lm')
    nd = sum(t >= x[3] for x in CHK); d.text((cw - 40, hh / 2), f'{nd} of 3', font=F('sb', 32), fill=GREY + (255,), anchor='rm')
    d.line([(32, hh), (cw - 32, hh)], fill=(60, 60, 60, 255), width=2)
    for i, (txt, meta, ts, td) in enumerate(CHK):
        y = hh + 15 + rh * i + rh / 2; x = 66; r = 26
        if t >= td:
            qq = eb((t - td) / 0.25); rr = r * (0.6 + 0.4 * qq)
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=GREEN + (255,)); fx.tick(d, x - rr * 0.5, y - rr * 0.45, rr, color=(0, 0, 0, 255), w=6)
            fc, mc = WHITE + (255,), GREEN + (255,)
        elif t >= ts:
            a0 = (t * 560) % 360; d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, 60), width=5)
            d.arc([x - r, y - r, x + r, y + r], a0, a0 + 110, fill=RED + (255,), width=6); fc, mc = WHITE + (255,), YELLOW + (255,)
        else:
            d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, 70), width=4); fc, mc = (255, 255, 255, 110), (150, 150, 150, 90)
        d.text((x + 50, y), txt, font=F('b', 40), fill=fc, anchor='lm')
        d.text((cw - 40, y), meta, font=F('xb', 26), fill=mc, anchor='rm')
    im = fx.shadowed(im, 26, 12, 150)
    fx.place(c, im, W / 2, c.H * 0.7 + (1 - q) * c.H * 0.08, 1, 0, al, guard=True)

def o_versus(c, t):
    s, e = 45.75, 48.22; lt = t - s
    if not (s <= t < e): return
    al = clamp((e - t) / 0.12)
    # CHIP MAKER
    k = clamp(lt / 0.1)
    if k > 0:
        f = F('xb', 110); s1 = 'CHIP MAKER'; w = int(f.getlength(s1) + 80)
        im = Image.new('RGBA', (w, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.rounded_rectangle([0, 0, w - 1, 159], 20, fill=WHITE + (255,))
        d.text((40, 14), s1, font=f, fill=BLACK + (255,))
        sc = 1.3 - 0.3 * eb(lt / 0.25); fx.place(c, fx.shadowed(im, 18, 8, 140), c.W / 2, c.H * 0.635, sc, -2, al * k, guard=True)
    k = clamp((lt - 0.8) / 0.1)
    if k > 0:
        im = text_layer('or', 'si', 150, GREEN, shadow=8); fx.place(c, im, c.W / 2, c.H * 0.712, 1.3 - 0.3 * eb((lt - 0.8) / 0.25), 0, al * k, guard=True)
    k = clamp((lt - 1.1) / 0.1)
    if k > 0:
        f = F('xb', 92); lines = ['NATIONAL', 'INFRASTRUCTURE?']
        w = int(max(f.getlength(x) for x in lines) + 70); h = 250
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        kk = eo((lt - 1.1) / 0.25); d.rectangle([0, 0, w * kk, h], fill=RED + (255,))
        for j, ln in enumerate(lines): d.text((35, 12 + j * 112), ln, font=f, fill=WHITE + (255,))
        sc = 1.2 - 0.2 * eb((lt - 1.1) / 0.25); fx.place(c, fx.shadowed(im, 18, 8, 140), c.W / 2, c.H * 0.812, sc, 1.5, al * k, guard=True)

def o_end(c, t):
    s = 48.22; lt = t - s
    if t < s: return
    k = clamp(lt / 0.15); c.img *= (1 - 0.55 * k)
    sc = 1.25 - 0.25 * eb(lt / 0.3)
    a = text_layer('Your', 'xb', 210, WHITE, shadow=10); b = text_layer('take?', 'si', 260, GREEN, shadow=10)
    wa, wb = F('xb', 210).getlength('Your'), F('si', 260).getlength('take?'); g = 40; x0 = (c.W - wa - g - wb) / 2
    fx.place(c, a, x0 + wa / 2, c.H * 0.7, sc, 0, k, guard=True)
    fx.place(c, b, x0 + wa + g + wb / 2, c.H * 0.7 + 8, sc, 0, clamp((lt - 0.08) / 0.12), guard=True)
    s2 = text_layer('Drop it in the comments  ↓', 'sb', 46, WHITE, shadow=6)
    fx.place(c, s2, c.W / 2, c.H * 0.79, 1, 0, clamp((lt - 0.25) / 0.15), guard=True)

def o_twist(c, t):
    s, e = 24.86, 25.66; lt = t - s
    if not (s <= t < e): return
    k = clamp(lt / 0.08); sc = 1.35 - 0.35 * eb(lt / 0.25)
    im = fx.text_img('the twist.', 190, 'serif', RED, glow=(RED, 22))
    fx.place(c, im, c.W / 2, c.H * 0.68, sc, -3, k * clamp((e - t) / 0.1), guard=True)

def o_private(c, t):
    s, e = 43.6, 44.95; lt = t - s
    if not (s <= t < e): return
    al = clamp((e - t) / 0.1)
    for j, (txt, kind, size, col, t0, yy) in enumerate([('who runs a', 'si', 120, WHITE, 0.0, 0.63), ('PRIVATE COMPANY?', 'xb', 104, WHITE, 0.35, 0.71)]):
        k = clamp((lt - t0) / 0.1)
        if k <= 0: continue
        if kind == 'xb':
            f = F('xb', size); w = int(f.getlength(txt) + 70); im = Image.new('RGBA', (w, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.rectangle([0, 0, w * eo((lt - t0) / 0.22), 149], fill=RED + (255,)); d.text((35, 14), txt, font=f, fill=WHITE + (255,))
        else: im = text_layer(txt, kind, size, col, shadow=10)
        fx.place(c, fx.shadowed(im, 16, 8, 150), c.W / 2, c.H * yy, 1.15 - 0.15 * eb((lt - t0) / 0.25), 0, al * k, guard=True)

OWN = [o_private, o_twist, o_days, o_gov, o_chyron, o_tape, o_checklist, o_versus, o_end]

def progress(c, t):
    k = clamp(t / DUR); h = 9
    c.img[0:h, :] = np.float32(BLACK) / 255 * 0.5 + c.img[0:h, :] * 0.5
    x = int(c.W * k)
    if x > 0: c.img[0:h, :x] = np.float32(GREEN) / 255

def base_grade(img):
    o = np.clip((img - 0.5) * 1.07 + 0.5, 0, 1)
    lum = (o @ np.float32([0.299, 0.587, 0.114]))[..., None]
    o = o + (1 - lum) * np.float32([-0.008, 0.004, 0.012]) + lum * np.float32([0.018, 0.006, -0.012])
    return np.clip(o, 0, 1)

# ---------------- render ----------------
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('trk'); ap.add_argument('words'); ap.add_argument('out')
    ap.add_argument('--still'); a = ap.parse_args()
    fr, fps, dur, sw, sh = fx.probe(a.src); W, H = 1080, 1920
    masks = np.load(a.trk + '_masks.npy', mmap_mode='r'); faces = np.load(a.trk + '_faces.npy'); sc = W / 540
    CH = chunks(load_words(a.words))
    fxs = [fx.Fx(dict(d), fps) for d in SKILL]
    stills = sorted({int(round(float(s) * fps)) for s in a.still.split(',')}) if a.still else None
    enc = None
    if not stills:
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fr), '-i', '-',
                                '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', a.out], stdin=subprocess.PIPE)
    for i, frame in enumerate(fx.read_frames(a.src, W, H, fr)):
        t = i / fps
        if stills is not None and i not in stills:
            if i > stills[-1]: break
            continue
        c = fx.Ctx(); c.W, c.H, c.t, c.fps = W, H, t, fps
        c.img = base_grade(frame.astype(np.float32) / 255.0)
        m = masks[min(i, len(masks) - 1)]
        c.m = cv2.resize(np.asarray(m), (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0
        fx_, fy_, fw_ = faces[min(i, len(faces) - 1)]; c.fx, c.fy, c.fw = fx_ * sc, fy_ * sc, fw_ * sc
        act = [f for f in fxs if f.start <= t < f.end]
        if cutaway(c, t): pass
        elif not any(f.name in CAMFX for f in act):
            for z0s, z0e, z0, z1 in ZOOMS:
                if z0s <= t < z0e: fx.face_cam(c, z0 + (z1 - z0) * eio((t - z0s) / (z0e - z0s)), 0.40); break
        for f in act:
            c.lt = t - f.start
            if f.name in FRONT_Y:
                m0, ah = c.m, fx.above_head; c.m = np.zeros_like(m0); yv = FRONT_Y[f.name] * H
                fx.above_head = lambda c_, h_: yv
                try: fx.EFFECTS[f.name][0](c, f)
                finally: c.m, fx.above_head = m0, ah
            else: fx.EFFECTS[f.name][0](c, f)
        for o in OWN: o(c, t)
        # split mode
        split_k = 0.0
        for s0, s1, name in SPLITS:
            if s0 <= t < s1:
                kin = 1.0 if s0 == 0 else eio((t - s0) / 0.3); kout = eio((s1 - t) / 0.28)
                split_k = min(kin, kout)
                shift = int(SHIFT * split_k)
                img = np.zeros_like(c.img); img[:] = np.float32(BLACK) / 255
                img[shift:] = c.img[:H - shift]
                c.img = img
                c.m = np.zeros((H, W), np.float32)
                pan = PANELS[name](W, t - s0)
                py = int(-P + P * split_k)
                fx.comp(c, pan, 0, py)
                break
        draw_caption(c, t, CH, split_k)
        progress(c, t)
        out = (np.clip(c.img, 0, 1) * 255 + 0.5).astype(np.uint8)
        if stills is not None:
            p = a.out.replace('.png', f'_{t:05.2f}.png'); cv2.imwrite(p, cv2.cvtColor(out, cv2.COLOR_RGB2BGR)); print('saved', p, flush=True)
        else:
            enc.stdin.write(out.tobytes())
            if i % int(fps * 5) == 0: print(f'  {t:5.1f}s', flush=True)
    if enc: enc.stdin.close(); enc.wait(); print('Done', a.out)

if __name__ == '__main__':
    main()
