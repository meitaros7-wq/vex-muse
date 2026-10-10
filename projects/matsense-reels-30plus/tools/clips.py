import subprocess, json, sys
S='/tmp/claude-0/-home-user/125b08d2-50fb-5053-bb52-ced3cc93e6f4/scratchpad'
A=S+'/ms/vid/A.mp4'; B=S+'/ms/vid/B.mp4'
OUT=sys.argv[1]
GRADE="eq=contrast=1.07:saturation=0.88:brightness=-0.025,colorbalance=rs=0.03:bs=-0.03:rm=0.02:bm=-0.02,vignette=PI/5"
GRAIN="noise=alls=3:allf=t"
def run(args): subprocess.run(['ffmpeg','-v','error','-y']+args,check=True)
def enc(): return ['-an','-c:v','libx264','-preset','slow','-crf','21','-pix_fmt','yuv420p','-r','30','-movflags','+faststart']
def track(t0,dur):
    o=subprocess.run(['python3',S+'/scripts/track.py',B,str(t0),str(dur)],capture_output=True,text=True).stdout
    return json.loads(o)
def lerp_expr(xs, step):
    # piecewise-linear crop-x expression (left edge), samples every `step` seconds
    e=str(xs[-1])
    for i in range(len(xs)-2,-1,-1):
        a,b=xs[i],xs[i+1]; t=i*step
        e=f"if(lt(t,{t+step:.2f}),{a:.1f}+({b-a:.1f})*(t-{t:.2f})/{step},{e})"
    return e
def b_vertical(name,t0,dur):
    c=track(t0,dur); xs=[min(max(c[i]-202.5,0),1280-405) for i in range(0,len(c),5)]
    x=lerp_expr(xs,0.5)
    run(['-ss',str(t0),'-i',B,'-t',str(dur),'-vf',f"crop=405:720:'{x}':0,scale=1080:1920:flags=lanczos,unsharp=5:5:0.7,{GRADE},{GRAIN}"]+enc()+[f'{OUT}/{name}.mp4'])
def a_vertical(name,t0,dur,zoom=1.0,cx=288,cy=512):
    w=int(576/zoom)//2*2; h=int(1024/zoom)//2*2
    x=max(0,min(576-w,cx-w//2)); y=max(0,min(1024-h,cy-h//2))
    run(['-ss',str(t0),'-i',A,'-t',str(dur),'-vf',f"crop={w}:{h}:{x}:{y},scale=1080:1920:flags=lanczos,unsharp=5:5:0.6,{GRADE},{GRAIN}"]+enc()+[f'{OUT}/{name}.mp4'])
def b_player(name,t0,dur,speed=1.0,w=960):
    h=w*9//16
    run(['-ss',str(t0),'-i',B,'-t',str(dur),'-vf',f"setpts=PTS/{speed},scale={w}:{h}:flags=lanczos,{GRADE}"]+enc()+[f'{OUT}/{name}.mp4'])
def a_player(name,t0,dur,speed=1.0,w=960,y=330):
    h=w*9//16
    # the athletes fill a landscape band of the portrait phone video: crop it, no pillarbox
    run(['-ss',str(t0),'-i',A,'-t',str(dur),'-vf',f"setpts=PTS/{speed},crop=576:324:0:{y},scale={w}:{h}:flags=lanczos,unsharp=5:5:0.6,{GRADE}"]+enc()+[f'{OUT}/{name}.mp4'])
    return
    fc=(f"[0:v]setpts=PTS/{speed},split[a][b];[a]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=20:2,eq=brightness=-0.15[bg];"
        f"[b]scale=-2:{h}[fg];[bg][fg]overlay=(W-w)/2:0,{GRADE}")
    run(['-ss',str(t0),'-i',A,'-t',str(dur),'-filter_complex',fc]+enc()+[f'{OUT}/{name}.mp4'])
jobs=sys.argv[2:] or ['all']
if 'all' in jobs or 'b' in jobs:
    b_vertical('v_b_352',352,9); b_vertical('v_b_406',406,10); b_vertical('v_b_258',258,10); b_vertical('v_b_020',20,8)
if 'all' in jobs or 'a' in jobs:
    a_vertical('v_a_full_330',330,10)
    a_vertical('v_a_335z',331,8,zoom=2.0,cx=160,cy=505)
    a_vertical('v_a_102z',98,8,zoom=2.0,cx=270,cy=485)
    a_vertical('v_a_258z',255,10,zoom=2.0,cx=165,cy=515)
    a_vertical('v_a_538z',533,8,zoom=2.0,cx=250,cy=500)
if 'all' in jobs or 'p' in jobs:
    b_player('p_b_406',406,10); b_player('p_b_352',350,10); b_player('p_b_ff',0,644,speed=24,w=640)
    a_player('p_a_538',532,10); a_player('p_a_258',256,10)
print('done')
