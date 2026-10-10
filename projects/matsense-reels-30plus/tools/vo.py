import json, re, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
C='/root/.cache/hyperframes/tts/'
k=Kokoro(C+'models/kokoro-v1.0.onnx', C+'voices/voices-v1.0.bin')
src=open(sys.argv[1]).read(); out=sys.argv[2]; voice=sys.argv[3]; speed=float(sys.argv[4])
ads=re.split(r'\n(?=AD \d)', src)[1:]
SR=24000
def trim(a, thr=0.008):
    idx=np.where(np.abs(a)>thr)[0]
    return a[max(idx[0]-240,0):idx[-1]+480] if len(idx) else a
meta={}
for block in ads:
    head,*rest=block.strip().split('\n')
    n=int(head.split()[1])
    lines=[l.strip() for l in rest if l.strip()]
    # join a line ending with ':' to the next
    j=[]
    for l in lines:
        if j and j[-1].endswith(':'): j[-1]+=' '+l
        else: j.append(l)
    pieces=[np.zeros(int(0.15*SR))]; t=0.15; info=[]
    for i,l in enumerate(j):
        pause_before = l.startswith('...')
        txt=l.lstrip('.').strip()
        if pause_before:
            pieces.append(np.zeros(int(0.7*SR))); t+=0.7
        a,sr=k.create(txt.replace('Matsense','Mat-sense'), voice=voice, speed=speed, lang='en-us'); assert sr==SR
        a=trim(a)
        info.append({'i':i,'text':txt,'start':round(t,3),'end':round(t+len(a)/SR,3)})
        pieces.append(a); t+=len(a)/SR
        gap = 0.55 if i==0 else (0.45 if txt.endswith('?') or txt.endswith('.') else 0.3)
        if i==len(j)-2: gap=0.6   # breath before the brand line
        if i<len(j)-1: pieces.append(np.zeros(int(gap*SR))); t+=gap
    pieces.append(np.zeros(int(0.3*SR)))
    y=np.concatenate(pieces).astype(np.float32)
    y=y/np.max(np.abs(y))*0.89
    sf.write(f'{out}/vo_ad{n}.wav', y, SR)
    meta[f'ad{n}']={'duration':round(len(y)/SR,3),'lines':info}
    print(n, round(len(y)/SR,2))
json.dump(meta, open(f'{out}/vo_lines.json','w'), indent=1)
