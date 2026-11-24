import sys, os, numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edit as E
W, H = 1080, 1920

def base(key, dark, zoom=1.0, dx=0.0, dy=0.0):
    o = E.photo_grade(E.cover(key, W, H, zoom, dx, dy), dark, 0.7)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    g = np.clip((yy - 0.42) * 2.4, 0, 1) * 0.92 + np.clip((0.12 - yy) * 5, 0, 1) * 0.6
    o = o * (1 - g)
    xx = np.linspace(-1, 1, W, dtype=np.float32)[None, :, None]; o = o * (1 - 0.35 * xx ** 2)
    im = Image.fromarray((np.clip(o, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    # subtle grain
    n = (np.random.default_rng(1).normal(0, 6, (H, W, 1)) * np.ones((1, 1, 3))).astype(np.int16)
    a = np.clip(np.asarray(im)[..., :3].astype(np.int16) + n, 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack([a, np.full((H, W), 255, np.uint8)]), 'RGBA')

def shadow_text(im, xy, s, f, fill, blur=14, a=200, anchor='la'):
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0], xy[1] + 6), s, font=f, fill=(0, 0, 0, a), anchor=anchor)
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur))); ImageDraw.Draw(im).text(xy, s, font=f, fill=fill, anchor=anchor)

def fit(s, kind, maxw, start):
    size = start
    while E.F(kind, size).getlength(s) > maxw: size -= 4
    return E.F(kind, size)

def cover_a(out):
    im = base('jensen_hook', 0.1, 1.0, 0.0, 0.02); d = ImageDraw.Draw(im); x0 = 72
    E.tag(d, x0, 300, 'BREAKING · NVIDIA', 38)
    f1 = fit('JENSEN', 'xb', W - 2 * x0, 330)
    shadow_text(im, (x0 - 8, 930), 'JENSEN', f1, E.WHITE + (255,), 20, 220)
    f2 = E.F('si', 250); shadow_text(im, (x0, 1175), 'is back.', f2, E.GREEN + (255,), 20, 220)
    d = ImageDraw.Draw(im); f3 = E.F('xb', 70); s3 = '11 DAYS AFTER HE QUIT'
    w3 = f3.getlength(s3); d.rectangle([x0, 1465, x0 + w3 + 56, 1465 + 104], fill=E.RED + (255,)); d.text((x0 + 28, 1476), s3, font=f3, fill=E.WHITE + (255,))
    f4 = E.F('sb', 46); d.text((x0, 1605), 'and Washington weighed in.', font=f4, fill=(235, 235, 235, 255))
    # yellow stock chip
    f5 = E.F('xb', 54); s5 = 'NVDA ≈ +30%'; w5 = f5.getlength(s5)
    chip = Image.new('RGBA', (int(w5 + 60), 96), (0, 0, 0, 0)); ImageDraw.Draw(chip).rounded_rectangle([0, 0, chip.width - 1, 95], 48, fill=E.YELLOW + (255,))
    ImageDraw.Draw(chip).text((30, 14), s5, font=f5, fill=E.BLACK + (255,)); chip = chip.rotate(6, Image.BICUBIC, expand=True)
    im.alpha_composite(E.fx.shadowed(chip, 16, 8, 160), (W - chip.width - 70, 800))
    d = ImageDraw.Draw(im); d.rectangle([0, 0, W, 10], fill=E.GREEN + (255,))
    im.convert('RGB').save(out, quality=95)

def cover_b(out):
    im = base('jensen_v', 0.12, 1.05, 0.0, 0.0); d = ImageDraw.Draw(im); x0 = 72
    E.tag(d, x0, 300, 'NOVEMBER 23 · NVIDIA', 38)
    f = fit('HE’S BACK.', 'xb', W - 2 * x0, 300)
    shadow_text(im, (x0 - 6, 1060), 'HE’S BACK.', f, E.WHITE + (255,), 20, 220)
    d = ImageDraw.Draw(im); f2 = E.F('xb', 92); s2 = 'BUT WHO DECIDED?'; w2 = f2.getlength(s2)
    d.rectangle([x0, 1330, x0 + w2 + 60, 1330 + 132], fill=E.RED + (255,)); d.text((x0 + 30, 1342), s2, font=f2, fill=E.WHITE + (255,))
    f3 = E.F('si', 96); shadow_text(im, (x0, 1500), 'Jensen Huang × Washington', f3, E.GREEN + (255,), 14, 220)
    d = ImageDraw.Draw(im); d.rectangle([0, 0, W, 10], fill=E.GREEN + (255,))
    im.convert('RGB').save(out, quality=95)

if __name__ == '__main__':
    o = sys.argv[1]; cover_a(o + '/reel_cover_A.jpg'); cover_b(o + '/reel_cover_B.jpg'); print('ok')
