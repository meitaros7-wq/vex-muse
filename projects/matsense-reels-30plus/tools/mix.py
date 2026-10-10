# Music bed + VO + SFX for one ad -> 48k stereo WAV at -14 LUFS. Usage: mix.py <ad#> <cues.json>
import json, sys, subprocess, numpy as np, soundfile as sf
R='/home/user/vex-muse/projects/matsense-reels-30plus'
n=sys.argv[1]; cue=json.load(open(sys.argv[2]))[f'ad{n}']
SR=48000; T=cue['duration']; N=int(T*SR); t=np.arange(N)/SR
def load(path):
    raw=subprocess.run(['ffmpeg','-v','error','-i',path,'-f','f32le','-ac','1','-ar',str(SR),'-'],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).copy()
rng=np.random.default_rng(int(n))
bpm=cue.get('bpm',100); beat=60/bpm; drop=cue['drop']; end=cue['end']
def env_ad(length, a, d):
    x=np.arange(length)/SR; return np.minimum(x/a,1)*np.exp(-x/d)
def add(buf, sig, at, g=1.0):
    i=int(at*SR); 
    if i>=len(buf): return
    j=min(len(buf), i+len(sig)); buf[i:j]+=sig[:j-i]*g
def lp(x, fc):  # one-pole lowpass
    a=np.exp(-2*np.pi*fc/SR); y=np.empty_like(x); s=0.0
    # vectorised via lfilter-free recursion in chunks
    from itertools import accumulate
    out=np.zeros_like(x); prev=0.0
    for k in range(0,len(x),4096):
        seg=x[k:k+4096]; o=np.empty_like(seg)
        for m in range(len(seg)):
            prev=(1-a)*seg[m]+a*prev; o[m]=prev
        out[k:k+4096]=o
    return out
bed=np.zeros(N,np.float32)
# chords (D minor): Dm  Bb  F  C, one per bar
roots=[38,34,41,36]; qual=[[0,3,7],[0,4,7],[0,4,7],[0,4,7]]
hz=lambda m: 440*2**((m-69)/12)
bar=4*beat
# pad: detuned saws, slow attack, filtered
pad=np.zeros(N,np.float32)
nb=int(np.ceil(T/bar))+1
for b in range(nb):
    r=roots[b%4]; q=qual[b%4]; t0=b*bar; L=int(bar*SR)+SR//2
    x=np.arange(L)/SR; e=np.minimum(x/0.5,1)*np.minimum(1,(bar+0.5-x)/0.5).clip(0,1)
    s=np.zeros(L)
    for iv in q:
        f=hz(r+12+iv)
        for dt in (-0.12,0.0,0.12):
            ph=2*np.pi*f*(1+dt/100)*x
            s+=((ph/np.pi)%2-1)*0.12
    add(pad, (s*e).astype(np.float32), t0)
pad=lp(pad, 900)
pad*=np.clip((t-0)/1.0,0,1)*0.55
# sub bass 8ths after the drop
sub=np.zeros(N,np.float32)
k=0
tt=drop
while tt<end:
    b=int(tt/bar); f=hz(roots[b%4]); L=int(beat/2*SR)
    x=np.arange(L)/SR; add(sub,(np.sin(2*np.pi*f*x)*env_ad(L,0.005,0.18)).astype(np.float32),tt,0.5)
    tt+=beat/2
# kick on beats after drop; soft heartbeat before
kick=np.zeros(N,np.float32)
def kik(g):
    L=int(0.45*SR); x=np.arange(L)/SR; f=45+75*np.exp(-x/0.04); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)*np.exp(-x/0.16)*g).astype(np.float32)
tt=0.0
while tt<drop:
    add(kick,kik(0.55),tt); add(kick,kik(0.35),tt+0.22); tt+=1.2*beat*2
tt=drop
while tt<end-0.01:
    add(kick,kik(0.9),tt); tt+=beat
# hats 8ths after drop
hat=np.zeros(N,np.float32)
noise=rng.standard_normal(int(0.06*SR)).astype(np.float32)
hn=noise-lp(noise,6000)
tt=drop+beat/2
while tt<end:
    add(hat,hn*env_ad(len(hn),0.001,0.02),tt,0.18); tt+=beat
bed=pad+sub+kick*0.9+hat
# end: let it ring and fade
fade=np.clip((T-t)/1.2,0,1)
after=t>=end
bed[after]*=np.exp(-(t[after]-end)/0.6)
bed=(bed*fade).astype(np.float32)
# VO and ducking
vo=load(f'{R}/audio/vo_ad{n}.wav'); vo=np.pad(vo,(0,max(0,N-len(vo))))[:N]
env=np.sqrt(np.convolve(vo**2,np.ones(2400)/2400,'same')); env=env/ (env.max()+1e-9)
duck=1-0.55*np.clip(env*3,0,1)
duck=np.convolve(duck,np.ones(4800)/4800,'same')
bed*=duck
sfx=np.zeros(N,np.float32)
for name,at,g in cue['sfx']:
    add(sfx, load(f'{R}/audio/sfx/{name}.mp3'), at, g)
def rms(x): return np.sqrt(np.mean(x**2)+1e-12)
bed*=0.16/ (rms(bed[int(drop*SR):int(end*SR)])+1e-9)*cue.get('bed_gain',1.0)
mix=vo*1.0+bed+sfx*0.55
mix=np.stack([mix,mix],1)
tmp=f'/tmp/claude-0/-home-user/125b08d2-50fb-5053-bb52-ced3cc93e6f4/scratchpad/mix_raw_{n}.wav'
sf.write(tmp, mix/ (np.abs(mix).max()+1e-9)*0.7, SR)
out=f'{R}/motion/reels/assets/audio/mix_ad{n}.wav'
subprocess.run(['ffmpeg','-v','error','-y','-i',tmp,'-af','loudnorm=I=-14:TP=-1.5:LRA=9','-ar','48000',out],check=True)
print('ok',out)
