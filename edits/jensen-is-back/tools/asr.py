import sys, json, subprocess, numpy as np, sherpa_onnx
src, out = sys.argv[1], sys.argv[2]
M = sys.argv[3]
pcm = subprocess.run(['ffmpeg','-v','error','-i',src,'-ac','1','-ar','16000','-f','s16le','-'],capture_output=True).stdout
a = np.frombuffer(pcm, np.int16).astype(np.float32)/32768
rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f'{M}/encoder.int8.onnx', decoder=f'{M}/decoder.int8.onnx', joiner=f'{M}/joiner.int8.onnx', tokens=f'{M}/tokens.txt', model_type='nemo_transducer', num_threads=4)
words=[]
CH=20*16000; i=0
while i < len(a):
    seg=a[i:i+CH+16000*0]
    # find a quiet cut point near the chunk end
    j=min(len(a), i+CH)
    if j<len(a):
        win=a[j-16000*3:j]; e=np.convolve(win**2, np.ones(800)/800, 'same'); j=j-16000*3+int(np.argmin(e))
    s=rec.create_stream(); s.accept_waveform(16000,a[i:j]); rec.decode_stream(s)
    r=s.result; off=i/16000
    cur=None
    for tok,t in zip(r.tokens, r.timestamps):
        if tok.startswith('▁') or tok.startswith(' ') or cur is None:
            if cur: words.append(cur)
            cur={'w':tok.lstrip('▁ '),'s':round(off+t,2)}
        else: cur['w']+=tok
    if cur: words.append(cur)
    i=j
for k,w in enumerate(words):
    w['e']=round(words[k+1]['s'] if k+1<len(words) else w['s']+0.4,2)
    w['e']=min(w['e'], w['s']+0.8)
json.dump(words, open(out,'w'), indent=0)
print(' '.join(f"{w['w']}@{w['s']}" for w in words))
