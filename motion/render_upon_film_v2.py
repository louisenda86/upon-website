#!/usr/bin/env python3
"""UpOn film V2: slow typography, real screens, and original calm ambient sound."""
from pathlib import Path
import argparse
import math
import subprocess
import wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT.parent / 'upon-macos/tmp/screenshots'
WORK = ROOT / 'motion/work/v2'
ASSETS = ROOT / 'dist/assets'
OUTPUT = ASSETS / 'upon-2.1-film-v2.mp4'
POSTER = ASSETS / 'upon-film-v2.jpg'
W, H, FPS, DURATION = 1920, 1080, 30, 30
WHITE, MUTED, BLUE = (247, 249, 252), (154, 169, 189), (31, 137, 255)
FONT = '/System/Library/Fonts/SFNS.ttf'
def font(size): return ImageFont.truetype(FONT, size)
def clamp(v): return max(0.0, min(1.0, v))
def smooth(v):
    v = clamp(v)
    return v*v*(3-2*v)
def centered(draw, y, text, size, color=WHITE):
    f = font(size)
    length = draw.textlength(text, font=f)
    draw.text(((W-length)/2, y), text, font=f, fill=color)
def wrapped(draw, xy, text, size, width, color=MUTED):
    words, lines, line = text.split(), [], ''
    f = font(size)
    for word in words:
        candidate = f'{line} {word}'.strip()
        if draw.textlength(candidate, font=f) > width and line:
            lines.append(line); line = word
        else: line = candidate
    lines.append(line)
    draw.multiline_text(xy, '\n'.join(lines), font=f, fill=color, spacing=13)
def opacity(item, value):
    result = item.copy()
    result.putalpha(result.getchannel('A').point(lambda a: round(a*clamp(value))))
    return result

def make_background():
    small = Image.new('RGB', (480, 270), (4, 8, 15))
    glow = Image.new('RGBA', small.size)
    d = ImageDraw.Draw(glow)
    d.ellipse((210,-80,530,220), fill=(0,115,255,65))
    d.ellipse((-130,150,190,420), fill=(62,83,125,30))
    glow = glow.filter(ImageFilter.GaussianBlur(58))
    small = small.convert('RGBA'); small.alpha_composite(glow)
    return small.resize((W,H), Image.Resampling.BICUBIC)
BACKGROUND = make_background()
ICON = Image.open(ROOT/'dist/assets/upon-icon.png').convert('RGBA').resize((138,138),Image.Resampling.LANCZOS)

def card(name, crop, width):
    source = Image.open(SHOTS/name).convert('RGB').crop(crop)
    height = round(source.height/source.width*width)
    shot = source.resize((width,height),Image.Resampling.LANCZOS).convert('RGBA')
    mask = Image.new('L',shot.size)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,width-1,height-1),28,fill=255)
    shot.putalpha(mask)
    frame = Image.new('RGBA',(width+100,height+100))
    shadow = Image.new('RGBA',frame.size)
    ImageDraw.Draw(shadow).rounded_rectangle((44,45,width+57,height+67),35,fill=(0,0,0,140))
    frame.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(24)))
    ImageDraw.Draw(frame).rounded_rectangle((43,43,width+57,height+57),35,fill=(19,27,40,255),outline=(255,255,255,55),width=2)
    frame.alpha_composite(shot,(50,50))
    return frame

IMPORT = card('upon-1.8-import-final.png',(310,220,875,731),830)
VERIFY = card('upon-1.7-biomarkers.png',(295,150,1105,577),990)
TIMELINE = card('upon-1.7-timeline.png',(301,155,1102,480),870)
PLAN = card('upon-1.7-plan.png',(303,155,1102,599),800)
ASK = card('upon-1.4-quick-chat.png',(393,255,1077,815),840)

def chrome(layer, label):
    d=ImageDraw.Draw(layer)
    d.text((94,62),'MEJALISM CORP',font=font(22),fill=(197,205,218))
    d.text((94,95),'UPON 2.1',font=font(15),fill=(114,132,156))
    length=d.textlength(label,font=font(18))
    d.text((W-94-length,68),label,font=font(18),fill=MUTED)

def copy(layer, label, title, body, x=125, y=282, width=665):
    d=ImageDraw.Draw(layer)
    d.text((x,y),label,font=font(24),fill=BLUE)
    d.multiline_text((x,y+74),title,font=font(100),fill=WHITE,spacing=0)
    box=d.multiline_textbbox((x,y+74),title,font=font(100),spacing=0)
    wrapped(d,(x,box[3]+52),body,31,width)

def intro(t):
    layer=BACKGROUND.copy(); chrome(layer,'A HEALTH WORKSPACE FOR YOUR MAC')
    enter=smooth(t/1.6)
    layer.alpha_composite(opacity(ICON,enter),(891,172+round(22*(1-enter))))
    d=ImageDraw.Draw(layer)
    centered(d,365,'UpOn 2.1',104)
    centered(d,502,'Clarity over time.',126,BLUE)
    centered(d,718,'Your reports. Your context. Your next step.',35,MUTED)
    d.line((W//2-190,845,W//2+round(190*enter),845),fill=(75,130,207),width=2)
    return layer

def import_scene(t):
    layer=BACKGROUND.copy(); chrome(layer,'01 / IMPORT')
    copy(layer,'BEGIN WITH YOUR REPORT','Bring it\ntogether.','Choose a PDF, image, spreadsheet or note. UpOn encrypts the original on your Mac.')
    scale=1.0+0.022*smooth(t/4.8)
    img=IMPORT.resize((round(IMPORT.width*scale),round(IMPORT.height*scale)),Image.Resampling.LANCZOS)
    layer.alpha_composite(img,(925,145-round(12*smooth(t/4.8))))
    return layer

def verify_scene(t):
    layer=BACKGROUND.copy(); chrome(layer,'02 / REVIEW')
    d=ImageDraw.Draw(layer)
    centered(d,167,'Review the numbers.',102)
    centered(d,305,'Local extraction first. Your verification next.',32,MUTED)
    layer.alpha_composite(VERIFY,((W-VERIFY.width)//2,410-round(16*smooth(t/4.3))))
    return layer

def trend_scene(t):
    layer=BACKGROUND.copy(); chrome(layer,'03 / UNDERSTAND')
    copy(layer,'CONTINUITY, WITH CONTEXT','See what\nchanged.','Compare reviewed biomarkers over time. Keep the original evidence beside every value.')
    graph=Image.new('RGBA',(900,660)); d=ImageDraw.Draw(graph)
    d.rounded_rectangle((0,0,899,659),40,fill=(16,24,38,238),outline=(255,255,255,34),width=2)
    d.text((52,46),'BIOMARKER TRAJECTORY',font=font(19),fill=MUTED)
    d.text((52,91),'A pattern, in perspective.',font=font(34),fill=WHITE)
    for y in (260,360,460):d.line((52,y,847,y),fill=(255,255,255,20),width=1)
    count=round(260*smooth((t+.15)/3.4)); points=[]
    for i in range(max(2,count)):
        p=i/259; y=464-193*p+42*math.sin(p*2*math.pi)
        points.append((52+round(790*p),round(y)))
    d.line(points,fill=BLUE,width=5,joint='curve')
    x,y=points[-1];d.ellipse((x-7,y-7,x+7,y+7),fill=WHITE)
    d.text((52,571),'Illustrative trajectory · no medical values',font=font(21),fill=MUTED)
    layer.alpha_composite(graph,(900,222))
    return layer

def story_scene(t):
    layer=BACKGROUND.copy();chrome(layer,'04 / TIMELINE + PLAN')
    d=ImageDraw.Draw(layer);centered(d,170,'The story behind the numbers.',92)
    centered(d,298,'Connect check-ups, milestones and practical next steps.',31,MUTED)
    layer.alpha_composite(TIMELINE,(75,430-round(14*smooth(t/4.4))))
    layer.alpha_composite(PLAN,(1035,440-round(8*smooth(t/4.4))))
    return layer

def ai_scene(t):
    layer=BACKGROUND.copy();chrome(layer,'05 / OPTIONAL AI')
    copy(layer,'ASK WHEN YOU ARE READY','Your model.\nYour choice.','OpenAI, Claude, Gemini or a local runtime. Review the data boundary and approve each analysis.',width=660)
    layer.alpha_composite(ASK,(935,199-round(15*smooth(t/4.5))))
    d=ImageDraw.Draw(layer);d.text((126,829),'Ollama · llama.cpp · LM Studio',font=font(25),fill=MUTED)
    return layer

def outro(t):
    layer=BACKGROUND.copy();chrome(layer,'BY LOUIS ENDA JAPAR')
    layer.alpha_composite(ICON,(891,195))
    d=ImageDraw.Draw(layer)
    centered(d,394,'Your health. In context.',107)
    centered(d,570,'UpOn 2.1 · Private beta for macOS',35,MUTED)
    d.rounded_rectangle((740,692,1180,785),25,fill=(0,112,244))
    centered(d,712,'Download the beta',32)
    centered(d,890,'MEJALISM CORP · BINTULU, SARAWAK',22,MUTED)
    centered(d,996,'Educational software · not medical advice',19,(108,124,146))
    return layer

SCENES=[(0,intro),(3.7,import_scene),(8.5,verify_scene),(12.8,trend_scene),(17.1,story_scene),(21.5,ai_scene),(26,outro)]
def frame(t):
    idx=max(i for i,(start,_) in enumerate(SCENES) if start<=t)
    start,draw=SCENES[idx]
    current=draw(t-start)
    if idx>0 and t-start<.85:
        old_start,old_draw=SCENES[idx-1]
        current=Image.blend(old_draw(t-old_start),current,smooth((t-start)/.85))
    if t<.75:current=Image.blend(BACKGROUND,current,smooth(t/.75))
    if t>29.45:current=Image.blend(current,BACKGROUND,smooth((t-29.45)/.55))
    return current.convert('RGB')

def audio():
    sr=48000;n=sr*DURATION;t=np.arange(n)/sr
    left=np.zeros(n);right=np.zeros(n)
    # Slow overlapping major-seventh/add-nine chords with soft attacks.
    chords=[(0,[130.8128,196,246.9417,293.6648]),(9,[174.6141,220,261.6256,329.6276]),(18,[130.8128,196,246.9417,293.6648])]
    for start,notes in chords:
        x=t-start
        env=np.where(x>=0,np.minimum(np.maximum(x,0)/3.4,1)*np.maximum(0,np.minimum((14-x)/4.5,1)),0)
        for j,f in enumerate(notes):
            breath=.89+.11*np.sin(2*np.pi*t/13+j)
            left+=env*breath*.043*np.sin(2*np.pi*f*t+j*.12)
            right+=env*breath*.043*np.sin(2*np.pi*f*t+j*.12+.028)
            left+=env*.009*np.sin(2*np.pi*f*2*t)
            right+=env*.009*np.sin(2*np.pi*f*2*t+.04)
    for start,f in [(1.4,523.251),(6.9,659.255),(12.8,587.329),(19.3,523.251),(25.4,783.991)]:
        x=t-start;active=np.maximum(x,0)
        env=np.where(x>=0,(1-np.exp(-active*8))*np.exp(-active*.7),0)
        tone=.043*env*(np.sin(2*np.pi*f*t)+.16*np.sin(2*np.pi*f*2*t))
        left+=tone;right+=tone*.92
    # A quiet stereo room tail; there are no ticks, drums or transition impacts.
    dry_left=left.copy();dry_right=right.copy()
    for delay,gain in [(.23,.16),(.41,.11),(.71,.065),(1.07,.035)]:
        shift=round(delay*sr)
        left[shift:]+=dry_right[:-shift]*gain
        right[shift:]+=dry_left[:-shift]*gain
    fade=np.minimum(t/2.5,1)*np.minimum((DURATION-t)/3,1)
    stereo=np.stack([left*fade,right*fade],axis=1)
    peak=np.max(np.abs(stereo));stereo*=.28/max(peak,1e-9)
    with wave.open(str(WORK/'calm-original.wav'),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
        w.writeframes((stereo*32767).astype('<i2').tobytes())

def preview():
    WORK.mkdir(parents=True,exist_ok=True);ASSETS.mkdir(exist_ok=True)
    sheet=Image.new('RGB',(1440,810))
    for i,t in enumerate([1.8,5.6,10.5,14.9,19.2,23.5,27.7,8.3,21.0]):
        still=frame(t);still.save(WORK/f'preview-{i+1}.jpg',quality=92)
        sheet.paste(still.resize((480,270)),((i%3)*480,(i//3)*270))
    sheet.save(WORK/'preview-contact.jpg',quality=92)
    frame(1.8).save(POSTER,quality=94,optimize=True)

def render():
    audio()
    cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p',str(WORK/'video.mp4')]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for i in range(DURATION*FPS):
        p.stdin.write(frame(i/FPS).tobytes())
        if i%(FPS*3)==0:print(f'Rendered {i/FPS:.0f}s / 30s',flush=True)
    p.stdin.close()
    if p.wait()!=0:raise RuntimeError('Video encoder failed')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(WORK/'video.mp4'),'-i',str(WORK/'calm-original.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t','30','-movflags','+faststart',str(OUTPUT)],check=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true')
    args=parser.parse_args();preview()
    if not args.preview:render()
