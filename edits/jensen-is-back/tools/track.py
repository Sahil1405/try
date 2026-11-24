import sys, numpy as np
sys.path.insert(0, sys.argv[3]); from fxload import fx
src, out = sys.argv[1], sys.argv[2]
fr, fps, dur, sw, sh = fx.probe(src); aw, ah = 540, 960
n = int(dur * fps) + 2
masks = np.lib.format.open_memmap(out + '_masks.npy', mode='w+', dtype=np.uint8, shape=(n, ah, aw))
trk = fx.Tracker(aw, ah); faces = []
for i, f in enumerate(fx.read_frames(src, aw, ah, fr)):
    m, face = trk(f, int(i / fps * 1000)); masks[i] = m; faces.append(face)
sm = fx.smooth(faces, fps)
np.save(out + '_faces.npy', sm); masks.flush(); print('frames', len(faces), 'face mean', sm.mean(0), 'min', sm.min(0), 'max', sm.max(0))
