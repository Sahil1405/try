"""Inbound vs Outbound post, redesigned in Meher Sayyed's two brand palettes.
usage: python post.py out_dir
"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')
IT, ISI = os.path.join(FD, 'InterTight[wght].ttf'), os.path.join(FD, 'InstrumentSerif-Italic.ttf')
W, H, S = 1080, 1350, 2  # design units, supersample factor
NAME, INIT = 'Meher Sayyed', 'MS'

PAL = {
    'softlight': dict(bg=(243, 236, 224), card=(220, 205, 180), card2=(232, 221, 202), ink=(42, 36, 32), sub=(112, 100, 88),
                      inb=(143, 165, 139), inb_ink=(42, 36, 32), out=(200, 69, 47), out_ink=(255, 255, 255), line=(214, 199, 175),
                      tile=(42, 36, 32), tile_ink=(243, 236, 224), tile_sub=(196, 184, 168), tile_line=(42, 36, 32),
                      chip=(243, 236, 224), chip_ink=(42, 36, 32), tchip=(66, 58, 52), tchip_ink=(243, 236, 224), dots=None, stat=(143, 165, 139)),
    'darkmode': dict(bg=(10, 10, 10), card=(22, 22, 22), card2=(28, 28, 28), ink=(255, 255, 255), sub=(150, 150, 150),
                     inb=(43, 255, 91), inb_ink=(10, 10, 10), out=(229, 16, 26), out_ink=(255, 255, 255), line=(42, 42, 42),
                     tile=(22, 22, 22), tile_ink=(255, 255, 255), tile_sub=(150, 150, 150), tile_line=(229, 16, 26),
                     chip=(38, 38, 38), chip_ink=(255, 255, 255), tchip=(38, 38, 38), tchip_ink=(255, 255, 255), dots=(30, 30, 30), stat=(255, 230, 0)),
}

INBOUND = [
    ('Search', [('Search visibility', 'Semrush', 'SEO + AEO')]),
    ('Content', [('Blog', 'PositiveSurfer', ''), ('LinkedIn', 'Canva', ''), ('YouTube', 'CapCut', ''), ('Newsletter', 'beehiiv', ''), ('Podcast', 'Riverside', '')]),
    ('Paid ads', [('Google Ads', 'Optmyzr', ''), ('Meta Ads', 'Madgicx', ''), ('LinkedIn Ads', 'Fibbler', ''), ('TikTok Ads', 'Revealbot', ''), ('YouTube Ads', 'Creatify', '')]),
    ('Relationships', [('Referrals', 'Crossbeam', ''), ('Community', 'Slack', ''), ('Webinars', 'Goldcast', ''), ('Events', 'Luma', '')]),
]
OUTBOUND = [('Cold email', 'Instantly'), ('Cold calling', 'Nooks'), ('LinkedIn DMs', 'HeyReach'), ('Gifting / direct mail', 'Sendoso'), ('Conferences / in-person', 'Bizzabo')]

_fc = {}
def font(kind, size):
    k = (kind, int(size * S))
    if k not in _fc:
        if kind == 'si': f = ImageFont.truetype(ISI, int(size * S))
        else:
            f = ImageFont.truetype(IT, int(size * S)); f.set_variation_by_axes([{'xb': 800, 'b': 700, 'sb': 600, 'm': 500, 'r': 400}[kind]])
        _fc[k] = f
    return _fc[k]


class C:
    def __init__(self, p):
        self.p = p; self.im = Image.new('RGBA', (W * S, H * S), p['bg'] + (255,)); self.d = ImageDraw.Draw(self.im)
        if p['dots']:
            for y in range(14, H, 28):
                for x in range(14, W, 28): self.d.ellipse([(x - 1.4) * S, (y - 1.4) * S, (x + 1.4) * S, (y + 1.4) * S], fill=p['dots'] + (255,))

    def tw(self, s, kind, size, track=0): return font(kind, size).getlength(s) / S + track * len(s)

    def text(self, x, y, s, kind, size, fill, anchor='la', track=0):
        f = font(kind, size)
        if track:
            if anchor[0] == 'r': x -= self.tw(s, kind, size, track)
            elif anchor[0] == 'm': x -= self.tw(s, kind, size, track) / 2
            for ch in s:
                self.d.text((x * S, y * S), ch, font=f, fill=fill + (255,), anchor='l' + anchor[1]); x += f.getlength(ch) / S + track
        else: self.d.text((x * S, y * S), s, font=f, fill=fill + (255,), anchor=anchor)

    def rr(self, x0, y0, x1, y1, r, fill=None, outline=None, width=0):
        self.d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], r * S, fill=fill + (255,) if fill else None,
                                 outline=outline + (255,) if outline else None, width=int(width * S))

    def circle(self, cx, cy, r, fill): self.d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=fill + (255,))

    def chip(self, x, cy, name, size=19, kind='m', bg=None, ink=None, r=14):
        """monogram dot + tool name. returns width"""
        p = self.p; bg = bg or p['chip']; ink = ink or p['chip_ink']
        self.circle(x + r, cy, r, bg); self.text(x + r, cy, name[0].upper(), 'xb', r * 1.05, ink, 'mm')
        self.text(x + 2 * r + 9, cy, name, kind, size, ink if kind != 'm' else ink, 'lm')
        return 2 * r + 9 + self.tw(name, kind, size)

    def tag(self, x, y, s, col=None, size=21):
        p = self.p; self.d.rectangle([x * S, (y + 3) * S, (x + 15) * S, (y + 18) * S], fill=p['out'] + (255,))
        self.text(x + 28, y + 11, s, 'sb', size, col or p['ink'], 'lm', track=2.2)

    def title_line(self, x, y, parts, anchor_mid=False):
        """parts: (text, kind, size, color, block_color or None). y = baseline"""
        tot = sum(self.tw(t, k, s) for t, k, s, c, b in parts)
        if anchor_mid: x = (W - tot) / 2
        for t, k, s, c, b in parts:
            w = self.tw(t, k, s)
            if b:
                f = font(k, s); bb = f.getbbox(t, anchor='ls')
                self.d.rectangle([x * S - s * 0.12 * S, y * S + bb[1] - s * 0.1 * S, x * S + bb[2] + s * 0.14 * S, y * S + bb[3] + s * 0.14 * S], fill=b + (255,))
            self.text(x, y, t, k, s, c, 'ls'); x += w
        return tot

    def footer(self, right_text, page=None):
        p = self.p; y = 1268
        self.d.line([(64 * S, (y - 22) * S), ((W - 64) * S, (y - 22) * S)], fill=p['line'] + (255,), width=2 * S)
        self.circle(64 + 28, y + 26, 28, p['out']); self.text(64 + 28, y + 27, INIT, 'xb', 21, p['out_ink'], 'mm')
        self.text(136, y + 26, NAME, 'xb', 29, p['ink'], 'lm')
        rt = right_text + (f'   {page}' if page else '')
        self.text(W - 64, y + 26, rt, 'sb', 21, p['sub'], 'rm')

    def save(self, path):
        self.im.convert('RGB').resize((W, H), Image.LANCZOS).save(path, quality=95); print('saved', path)


def fit_size(c, parts_fn, maxw, start):
    s = start
    while sum(c.tw(t, k, sz) for t, k, sz, *_ in parts_fn(s)) > maxw: s -= 2
    return s


# ---------------- format A: one-page cheat sheet (intent spectrum + grid) ----------------
def single(p, out):
    c = C(p); L, R = 64, W - 64
    c.tag(L, 62, 'GO-TO-MARKET CHEAT SHEET', p['sub'])
    mk = lambda s: [('Inbound', 'xb', s, p['ink'], None), (' vs. ', 'si', s * 1.08, p['ink'], None), ('Outbound.', 'xb', s, p['out_ink'], p['out'])]
    s = fit_size(c, mk, R - L - 20, 120); c.title_line(L, 200, mk(s))
    # intent spectrum
    y = 262
    c.text(L, y, 'Already looking', 'sb', 21, p['ink'], 'lm'); c.text(R, y, 'Not looking yet', 'sb', 21, p['ink'], 'rm')
    c.text(W / 2, y, 'BUYER INTENT', 'sb', 17, p['sub'], 'mm', track=2.5)
    bx0, bx1, by = L, R, y + 26
    grad = Image.new('RGBA', (int((bx1 - bx0) * S), int(12 * S)))
    gd = ImageDraw.Draw(grad)
    for i in range(grad.width):
        u = i / grad.width; k = min(1, max(0, (u - 0.35) / 0.3)); col = tuple(int(p['inb'][j] * (1 - k) + p['out'][j] * k) for j in range(3))
        gd.line([(i, 0), (i, grad.height)], fill=col + (255,))
    m = Image.new('L', grad.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, grad.width - 1, grad.height - 1], 6 * S, fill=255); grad.putalpha(m)
    c.im.alpha_composite(grad, (int(bx0 * S), int(by * S)))
    # inbound header
    y = 338
    pw = c.tw('INBOUND', 'xb', 22, 2) + 40; c.rr(L, y, L + pw, y + 46, 23, p['inb']); c.text(L + pw / 2, y + 24, 'INBOUND', 'xb', 22, p['inb_ink'], 'mm', track=2)
    c.text(L + pw + 18, y + 25, 'They find you.', 'si', 40, p['ink'], 'lm')
    c.text(R, y + 24, '15 channels', 'sb', 20, p['sub'], 'rm')
    # three cards
    cols = [[INBOUND[0], INBOUND[3]], [INBOUND[1]], [INBOUND[2]]]
    gap = 16; cw = (R - L - 2 * gap) / 3; cy0, cy1 = 404, 872; rh = 64
    for ci, groups in enumerate(cols):
        x0 = L + ci * (cw + gap); c.rr(x0, cy0, x0 + cw, cy1, 24, p['card'])
        yy = cy0 + 22
        for gname, rows in groups:
            c.d.rectangle([(x0 + 22) * S, (yy + 5) * S, (x0 + 32) * S, (yy + 15) * S], fill=p['inb'] + (255,)) if p['dots'] else c.d.rectangle([(x0 + 22) * S, (yy + 5) * S, (x0 + 32) * S, (yy + 15) * S], fill=p['ink'] + (255,))
            c.text(x0 + 42, yy + 10, gname.upper(), 'sb', 16, p['sub'], 'lm', track=2.2); yy += 32
            for j, (ch, tool, note) in enumerate(rows):
                c.text(x0 + 22, yy + 6, ch, 'b', 22, p['ink'], 'lt')
                if note: c.text(x0 + 24 + c.tw(ch, 'b', 22), yy + 9, f'  {note}', 'm', 14, p['sub'], 'lt')
                c.chip(x0 + 22, yy + 45, tool, 18, 'm', p['chip'], p['chip_ink'], 12)
                yy += rh
                if j < len(rows) - 1: c.d.line([((x0 + 22) * S, (yy - 2) * S), ((x0 + cw - 22) * S, (yy - 2) * S)], fill=p['line'] + (255,), width=S)
            yy += 18
    # outbound header
    y = 900
    pw = c.tw('OUTBOUND', 'xb', 22, 2) + 40; c.rr(L, y, L + pw, y + 46, 23, p['out']); c.text(L + pw / 2, y + 24, 'OUTBOUND', 'xb', 22, p['out_ink'], 'mm', track=2)
    c.text(L + pw + 18, y + 25, 'You find them.', 'si', 40, p['ink'], 'lm')
    c.text(R, y + 24, '5 channels', 'sb', 20, p['sub'], 'rm')
    tw_ = (R - L - 4 * 12) / 5; ty0, ty1 = 964, 1206
    for i, (ch, tool) in enumerate(OUTBOUND):
        x0 = L + i * (tw_ + 12)
        c.rr(x0, ty0, x0 + tw_, ty1, 22, p['tile'], p['tile_line'], 2)
        c.text(x0 + 18, ty0 + 20, f'0{i + 1}', 'xb', 34, p['out'], 'lt')
        words = ch.split(' '); lines, cur = [], ''
        for wd in words:
            t = (cur + ' ' + wd).strip()
            if c.tw(t, 'b', 22) > tw_ - 34 and cur: lines.append(cur); cur = wd
            else: cur = t
        lines.append(cur)
        for k, ln in enumerate(lines): c.text(x0 + 18, ty0 + 78 + k * 28, ln, 'b', 22, p['tile_ink'], 'lt')
        c.chip(x0 + 18, ty1 - 34, tool, 17, 'm', p['tchip'], p['tchip_ink'], 12)
    c.footer('Save this for later ↗')
    c.save(out)


# ---------------- format B: 4-slide carousel ----------------
def slide_cover(p, out):
    c = C(p); L = 64
    c.tag(L, 62, 'GO-TO-MARKET · 20 CHANNELS', p['sub'])
    c.title_line(L, 470, [('Inbound', 'xb', 230, p['ink'], None)])
    c.title_line(L + 6, 690, [('vs.', 'si', 260, p['inb'] if p['dots'] else p['out'], None)])
    so = fit_size(c, lambda z: [('Outbound.', 'xb', z, None, None)], W - 2 * L - 40, 200)
    c.title_line(L + 14, 900, [('Outbound.', 'xb', so, p['out_ink'], p['out'])])
    c.text(L, 1010, 'Every channel worth running,', 'm', 42, p['ink'], 'lt')
    c.text(L, 1062, 'and one tool to run each.', 'si', 52, p['sub'], 'lt')
    c.footer('Swipe →', '1/4'); c.save(out)


def slide_inbound(p, out):
    c = C(p); L, R = 64, W - 64
    pw = c.tw('INBOUND', 'xb', 24, 2) + 44; c.rr(L, 70, L + pw, 120, 25, p['inb']); c.text(L + pw / 2, 96, 'INBOUND', 'xb', 24, p['inb_ink'], 'mm', track=2)
    c.text(L, 250, 'They find you.', 'si', 120, p['ink'], 'ls')
    c.text(L, 300, 'For people already looking.', 'm', 32, p['sub'], 'lm')
    colw = (R - L - 28) / 2; rh = 56
    layout = [(L, [INBOUND[1], INBOUND[0]]), (L + colw + 28, [INBOUND[2], INBOUND[3]])]
    for x0, groups in layout:
        yy = 360
        for gname, rows in groups:
            c.text(x0, yy + 12, gname.upper(), 'sb', 18, p['sub'], 'lm', track=2.4); yy += 34
            c.rr(x0, yy, x0 + colw, yy + rh * len(rows) + 8, 20, p['card'])
            for j, (ch, tool, note) in enumerate(rows):
                cy = yy + 4 + rh * j + rh / 2
                c.text(x0 + 22, cy, ch, 'b', 24, p['ink'], 'lm')
                tl = c.tw(tool, 'm', 19) + 24 + 9; c.chip(x0 + colw - 22 - tl, cy, tool, 19, 'm', p['chip'], p['chip_ink'], 12)
                if j < len(rows) - 1: c.d.line([((x0 + 22) * S, (cy + rh / 2) * S), ((x0 + colw - 22) * S, (cy + rh / 2) * S)], fill=p['line'] + (255,), width=S)
            yy += rh * len(rows) + 8 + 30
        last_y = yy
    # stat callout under the shorter (left) column
    x0 = L; y0 = 360 + 34 + rh * 5 + 8 + 30 + 34 + rh * 1 + 8 + 30
    c.rr(x0, y0, x0 + colw, 1206, 24, p['card2'] if not p['dots'] else (22, 22, 22), p['stat'], 2)
    c.text(x0 + 28, y0 + 30, '15', 'xb', 150, p['stat'] if p['dots'] else p['out'], 'lt')
    c.text(x0 + 30, y0 + 210, 'ways to get found', 'si', 46, p['ink'], 'lt')
    c.text(x0 + 30, y0 + 268, 'by buyers who already', 'm', 24, p['sub'], 'lt'); c.text(x0 + 30, y0 + 300, 'want what you sell.', 'm', 24, p['sub'], 'lt')
    c.footer('Swipe →', '2/4'); c.save(out)


def slide_outbound(p, out):
    c = C(p); L, R = 64, W - 64
    pw = c.tw('OUTBOUND', 'xb', 24, 2) + 44; c.rr(L, 70, L + pw, 120, 25, p['out']); c.text(L + pw / 2, 96, 'OUTBOUND', 'xb', 24, p['out_ink'], 'mm', track=2)
    c.text(L, 250, 'You find them.', 'si', 120, p['ink'], 'ls')
    c.text(L, 300, 'For people who aren’t looking yet.', 'm', 32, p['sub'], 'lm')
    rh = 160; gap = 14; y0 = 360
    for i, (ch, tool) in enumerate(OUTBOUND):
        y = y0 + i * (rh + gap)
        c.rr(L, y, R, y + rh, 26, p['tile'], p['tile_line'], 2)
        c.text(L + 34, y + rh / 2, f'0{i + 1}', 'xb', 70, p['out'], 'lm')
        c.text(L + 170, y + rh / 2 - 22, ch, 'xb', 40, p['tile_ink'], 'lm')
        c.text(L + 172, y + rh / 2 + 28, 'Tool to run it', 'm', 20, p['tile_sub'], 'lm')
        tl = c.tw(tool, 'sb', 26) + 40 + 12
        c.rr(R - 30 - tl - 18, y + rh / 2 - 34, R - 30, y + rh / 2 + 34, 34, p['tchip'])
        c.chip(R - 30 - tl - 6, y + rh / 2, tool, 26, 'sb', p['out'], p['tchip_ink'], 20)
    c.footer('Swipe →', '3/4'); c.save(out)


def slide_compare(p, out):
    c = C(p); L, R = 64, W - 64
    c.tag(L, 62, 'SO, WHICH LANE FIRST?', p['sub'])
    c.title_line(L, 250, [('Pick by ', 'xb', 104, p['ink'], None), ('intent.', 'si', 116, p['ink'], None)])
    colw = (R - L - 24) / 2; y0, y1 = 320, 900
    rows = [('Who you reach', 'People already searching', 'People who don’t know you yet'),
            ('Who moves first', 'They come to you', 'You go to them'),
            ('Pace', 'Compounds over time', 'Starts conversations now'),
            ('Works best when', 'Demand already exists', 'You need pipeline fast')]
    for k, (name, col, ink, head) in enumerate([('INBOUND', p['inb'], p['inb_ink'], 0), ('OUTBOUND', p['out'], p['out_ink'], 1)]):
        x0 = L + k * (colw + 24)
        c.rr(x0, y0, x0 + colw, y1, 26, p['card'] if k == 0 else p['tile'], None if k == 0 else p['tile_line'], 0 if k == 0 else 2)
        c.rr(x0 + 24, y0 + 24, x0 + 24 + c.tw(name, 'xb', 22, 2) + 40, y0 + 70, 23, col); c.text(x0 + 44, y0 + 48, name, 'xb', 22, ink, 'lm', track=2)
        tcol = p['ink'] if k == 0 else p['tile_ink']; scol = p['sub'] if k == 0 else p['tile_sub']
        for j, r in enumerate(rows):
            yy = y0 + 110 + j * 118
            c.text(x0 + 28, yy, r[0].upper(), 'sb', 15, scol, 'lt', track=2)
            words = r[1 + k].split(' '); lines, cur = [], ''
            for wd in words:
                t = (cur + ' ' + wd).strip()
                if c.tw(t, 'b', 30) > colw - 56 and cur: lines.append(cur); cur = wd
                else: cur = t
            lines.append(cur)
            for q, ln in enumerate(lines): c.text(x0 + 28, yy + 28 + q * 36, ln, 'b', 30, tcol, 'lt')
    c.title_line(L, 1010, [('The best teams run ', 'xb', 62, p['ink'], None), ('both.', 'xb', 62, p['out_ink'], p['out'])])
    c.text(L, 1080, 'Save this and share it with your team.', 'si', 44, p['sub'], 'lt')
    c.footer('Follow for more', '4/4'); c.save(out)


if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for key, p in PAL.items():
        single(p, f'{out}/{key}_single.jpg')
        slide_cover(p, f'{out}/{key}_carousel_1.jpg'); slide_inbound(p, f'{out}/{key}_carousel_2.jpg')
        slide_outbound(p, f'{out}/{key}_carousel_3.jpg'); slide_compare(p, f'{out}/{key}_carousel_4.jpg')
