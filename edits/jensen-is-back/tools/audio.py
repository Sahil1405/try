import numpy as np, sys, wave
SR = 44100; DUR = 49.2; N = int(SR * DUR)
rng = np.random.default_rng(7)
def env_exp(n, tau): return np.exp(-np.arange(n) / (tau * SR))
def lp(x, a):  # one-pole lowpass, a scalar or per-sample array in (0,1]
    y = np.zeros_like(x); s = 0.0; a = np.broadcast_to(a, x.shape)
    for i in range(len(x)): s += a[i] * (x[i] - s); y[i] = s
    return y
def hp(x, a): return x - lp(x, a)
def chirp(f0, f1, dur, curve=1.0):
    n = int(dur * SR); f = f0 + (f1 - f0) * (np.linspace(0, 1, n) ** curve); return np.sin(2 * np.pi * np.cumsum(f) / SR)
def norm(x, peak): return x / (np.abs(x).max() + 1e-9) * peak
def whoosh(dur=0.42, up=True):
    n = int(dur * SR); u = np.linspace(0, 1, n); nz = rng.standard_normal(n)
    cut = (0.02 + 0.25 * (u if up else 1 - u) ** 1.5) if up else (0.27 - 0.25 * u)
    x = hp(lp(nz, cut), 0.01); return norm(x * np.sin(np.pi * u) ** 2, 0.55)
def pop(f=700):
    x = chirp(f * 0.6, f * 1.6, 0.07, 0.5) * env_exp(int(0.07 * SR), 0.018); return norm(x, 0.5)
def tick(): n = int(0.012 * SR); return norm(hp(rng.standard_normal(n), 0.5) * env_exp(n, 0.002), 0.25)
def thud(f0=110, f1=42, dur=0.4, peak=0.8):
    n = int(dur * SR); x = chirp(f0, f1, dur, 0.4) * env_exp(n, dur / 4)
    c = lp(rng.standard_normal(n), 0.15) * env_exp(n, 0.01) * 0.6; return norm(x + c, peak)
def stamp(): x = thud(140, 38, 0.6, 0.9); n = int(0.09 * SR); x[:n] += lp(rng.standard_normal(n), 0.4) * env_exp(n, 0.02) * 0.5; return norm(x, 0.95)
def ding():
    n = int(0.9 * SR); t = np.arange(n) / SR; x = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((1318.5, 1), (1975.5, 0.6), (2637, 0.3)))
    return norm(x * env_exp(n, 0.22) * (1 - np.exp(-t / 0.002)), 0.32)
def check(): a = ding()[: int(0.35 * SR)] * env_exp(int(0.35 * SR), 0.08); return norm(np.concatenate([pop(900)[:int(0.03 * SR)] * 0.6, a]), 0.35)
def riser(dur=1.3):
    n = int(dur * SR); u = np.linspace(0, 1, n); nz = lp(rng.standard_normal(n), 0.02 + 0.4 * u ** 2)
    x = nz * 0.7 + chirp(180, 900, dur, 2) * 0.25; return norm(x * u ** 2.2, 0.5)
def boom(): n = int(1.6 * SR); x = chirp(70, 32, 1.6, 0.3) * env_exp(n, 0.45); x[:int(0.05 * SR)] += lp(rng.standard_normal(int(0.05 * SR)), 0.3) * 0.5; return norm(x, 0.95)
def scribble(dur=0.9):
    n = int(dur * SR); nz = hp(lp(rng.standard_normal(n), 0.35), 0.08)
    am = np.abs(np.sin(2 * np.pi * np.cumsum(9 + 6 * rng.random(n)) / SR)) ** 2; return norm(nz * am * np.sin(np.pi * np.linspace(0, 1, n)) ** 0.5, 0.3)
def slap(): n = int(0.12 * SR); x = lp(rng.standard_normal(n), 0.5) * env_exp(n, 0.015); return norm(x + thud(160, 70, 0.12, 0.5)[:n] * 0.6, 0.7)

sfx = np.zeros(N)
def at(t, x, g=1.0):
    i = int(t * SR); j = min(N, i + len(x)); sfx[i:j] += x[: j - i] * g
at(0.0, boom(), 0.55); at(0.08, pop(500)); at(0.64, pop(560)); at(1.12, pop(640)); at(1.44, thud(), 0.5)
at(2.1, whoosh(0.4)); at(2.32, pop(800), 0.8)
for k in range(11): at(2.36 + k * 0.05, tick(), 0.7)
at(4.3, whoosh(0.3)); at(4.38, thud(120, 50, 0.3, 0.6))
at(5.75, whoosh(0.45)); at(7.36, thud(), 0.8); at(9.2, pop(600), 0.7)
at(10.7, whoosh(0.35, False)); at(10.96, stamp())
at(12.15, whoosh(0.3)); at(12.4, pop(900), 0.6)
at(16.5, whoosh(0.2), 0.8); at(16.5, scribble(0.25), 0.8)
at(17.75, whoosh(0.45)); at(20.2, pop(700), 0.7); at(21.08, thud(), 0.8); at(21.8, whoosh(0.35, False))
at(22.02, pop(800), 0.7); at(23.9, ding(), 0.9)
at(23.2, riser(1.25)); at(24.44, boom(), 0.9); at(24.86, thud(90, 40, 0.5, 0.8))
at(25.42, whoosh(0.45)); at(27.96, thud(), 0.7); at(29.32, pop(650), 0.8); at(29.7, whoosh(0.35, False))
at(29.86, whoosh(0.25), 0.7)
at(31.08, slap()); at(31.85, slap())
at(33.1, whoosh(0.4)); at(33.8, pop(700), 0.6)
at(35.45, pop(600), 0.7); at(37.5, check()); at(39.9, check()); at(41.35, check())
at(41.97, scribble(0.85)); at(43.0, scribble(0.3), 0.7)
at(45.75, pop(700)); at(46.55, pop(500), 0.8); at(46.85, thud(), 0.8)
at(48.0, riser(0.25), 0.5); at(48.22, boom(), 0.7); at(48.25, pop(900))

# music bed: dark pulse, 96 bpm
t = np.arange(N) / SR; bed = np.zeros(N); beat = 60 / 96
drone = (np.sin(2 * np.pi * 55 * t) * 0.5 + np.sin(2 * np.pi * 110 * t) * 0.15) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * t))
pad = np.zeros(N)
chords = [(220, 261.63, 329.63), (174.61, 220, 261.63), (196, 246.94, 293.66), (164.81, 207.65, 246.94)]
bar = beat * 4
for ci in range(int(DUR / (bar * 2)) + 1):
    ch = chords[ci % 4]; i0 = int(ci * bar * 2 * SR); i1 = min(N, int((ci + 1) * bar * 2 * SR))
    if i0 >= N: break
    tt = np.arange(i1 - i0) / SR; e = np.minimum(1, tt / 1.2) * np.minimum(1, (tt[-1] - tt) / 0.8 + 0.05)
    pad[i0:i1] = sum(np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) for f in ch) * e / 3
pad = lp(pad, 0.08)
kick = thud(120, 45, 0.28, 1.0); hat = norm(hp(rng.standard_normal(int(0.03 * SR)), 0.6) * env_exp(int(0.03 * SR), 0.006), 1.0)
k_t = 2.28
while k_t < 48.2:
    if not (24.44 <= k_t < 25.66):
        i = int(k_t * SR); j = min(N, i + len(kick)); bed[i:j] += kick[: j - i] * 0.9
        i = int((k_t + beat / 2) * SR); j = min(N, i + len(hat)); bed[i:j] += hat[: j - i] * 0.18
    k_t += beat
gate = np.ones(N); gate[int(24.44 * SR):int(25.66 * SR)] = 0.15
fade = np.minimum(1, t / 0.4) * np.clip((49.1 - t) / 0.9, 0, 1)
music = (drone * 0.35 + pad * 0.3) * gate * fade + bed * fade
music = norm(music, 0.6)
def wr(p, x):
    x = np.clip(x, -1, 1); w = wave.open(p, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()
wr(sys.argv[1] + '_sfx.wav', norm(sfx, 0.9)); wr(sys.argv[1] + '_music.wav', music); print('ok')
