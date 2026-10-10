# Track the white-gi athlete's x in match B to drive a 9:16 crop. Prints per-0.1s centers as JSON.
import subprocess, numpy as np, json, sys
src, t0, dur = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
W,H=320,180
cmd=['ffmpeg','-v','error','-ss',str(t0),'-i',src,'-t',str(dur),'-vf',f'fps=10,scale={W}:{H}','-f','rawvideo','-pix_fmt','rgb24','-']
raw=subprocess.run(cmd,capture_output=True).stdout
fr=np.frombuffer(raw,np.uint8).reshape(-1,H,W,3).astype(np.int16)
xs=[]; prev=W*0.5
for f in fr:
    r,g,b=f[...,0],f[...,1],f[...,2]
    mx=f.max(-1); mn=f.min(-1)
    white=(mn>150)&((mx-mn)<45)
    dark=(mx<60)  # black belts/referee/hair
    m=np.zeros((H,W),bool); m[70:170]=white[70:170]
    ys,xx=np.nonzero(m)
    if len(xx)>15:
        # prefer the cluster nearest the previous center
        w=np.exp(-((xx-prev)/60.0)**2)
        c=float((xx*w).sum()/w.sum()) if w.sum()>1 else float(np.median(xx))
    else: c=prev
    xs.append(c); prev=c
xs=np.array(xs)
# smooth
k=np.ones(9)/9; pad=np.pad(xs,4,mode='edge'); sm=np.convolve(pad,k,'valid')
print(json.dumps([round(float(v)*1280/W,1) for v in sm]))
