#!/usr/bin/env python3
import math, random, time, tkinter as tk
W,H=960,540
def clamp(x,a,b): return a if x<a else b if x>b else x
def g(v): v=clamp(int(v),0,255); return f"#{v:02x}{v:02x}{v:02x}"
class Idle:
  def __init__(s,r):
    r.title("HOLY DIVER — idle (BWL)"); r.resizable(False,False)
    s.c=tk.Canvas(r,width=W,height=H,bg="black",highlightthickness=0); s.c.pack()
    s.t0=time.time(); s.dt=1/60; s.d=0.0; s.v=18.0
    s.ha=1.0; s.ht=1.0; s.htm=0.0; s.w=[]; s.gh=[]; s.ghm=120
    s.st=[{"x":random.random()*W,"y":random.random()*H,"s":0.6+random.random()*1.6,"p":0.15+random.random()*0.9,"ph":random.random()*math.tau} for _ in range(140)]
    s.bd=[{"y0":(i/8)*H,"h":H/8,"p":0.35+(i/7)*0.9} for i in range(8)]
    s.gu=[{"x":(random.uniform(-70,120) if random.random()<0.5 else random.uniform(W-120,W+70)),"y":random.uniform(0,H),"r":random.uniform(10,22),"ph":random.random()*math.tau} for _ in range(14)]
    for k in ("<space>","<Return>","z","x","c"): r.bind(k,s.hit)
    r.bind("h",s.hush); r.bind("r",s.reset)
    s.tick(r)
  def now(s): return time.time()-s.t0
  def reset(s,*_): s.t0=time.time(); s.d=0.0; s.v=18.0; s.ha=1.0; s.ht=1.0; s.htm=0.0; s.w.clear(); s.gh.clear()
  def hush(s,*_): s.htm=1.2; s.ht=0.0
  def pos(s):
    t=s.now(); return W*0.52+math.sin(t*0.82)*13, H*0.54+math.sin(t*0.61+1.7)*9
  def hit(s,*_):
    x,y=s.pos(); s.w.append({"x":x,"y":y,"r":2.0,"dr":520.0,"t":0.0,"life":0.55})
    s.v=min(s.v+2.2,70.0); s.ht=max(s.ht,0.35); s.htm=max(s.htm,0.18)
  def tick(s,r):
    t=s.now(); s.d+=s.v*s.dt; s.v+=(18.0-s.v)*0.015
    if s.htm>0: s.htm-=s.dt; 
    if s.htm<=0: s.ht=1.0
    s.ha=clamp(s.ha+(s.ht-s.ha)*0.09,0.0,1.0)
    nw=[]
    for w in s.w: w["t"]+=s.dt; w["r"]+=w["dr"]*s.dt; 
    for w in s.w:
      if w["t"]<w["life"]: nw.append(w)
    s.w=nw
    x,y=s.pos(); s.gh.append((x,y,t)); s.gh=s.gh[-s.ghm:]
    s.draw(t); r.after(int(s.dt*1000), lambda: s.tick(r))
  def draw(s,t):
    c=s.c; c.delete("all")
    lx=W*0.50+math.sin(t*0.22)*130; ly=H*0.56+math.sin(t*0.18+0.9)*45
    c.create_oval(lx-260,ly-140,lx+260,ly+140,fill=g(13),outline="")
    c.create_oval(lx-210,ly-112,lx+210,ly+112,fill=g(17),outline="")
    c.create_oval(lx-150,ly-80,lx+150,ly+80,fill=g(20),outline="")
    for s0 in s.st:
      yy=(s0["y"]+s.d*s0["p"])%H; xx=(s0["x"]+math.sin(t*0.10+s0["ph"])*0.6)%W; rr=s0["s"]
      b=clamp(140+60*math.sin(t*0.55+s0["x"]*0.01+s0["ph"]),90,220)
      c.create_oval(xx-rr,yy-rr,xx+rr,yy+rr,fill=g(b),outline="")
    for i,b0 in enumerate(s.bd):
      yy=(b0["y0"]+s.d*b0["p"])%H; base=clamp(10+i*6,6,60)
      c.create_rectangle(0,yy,W,yy+b0["h"],fill=g(base),outline="")
    for g0 in s.gu:
      yy=(g0["y"]+s.d*0.85)%H; xx=g0["x"]+math.sin(t*0.48+g0["ph"])*8
      flick=0.5+0.5*math.sin(t*1.2+g0["ph"]+(s.d/1600.0))
      if flick<0.20: continue
      rr=g0["r"]*(0.75+0.30*flick); v=clamp(120+100*flick,110,230)
      c.create_oval(xx-rr,yy-rr*0.42,xx+rr,yy+rr*0.42,fill=g(v),outline="")
    if len(s.gh)>4:
      for i in range(1,len(s.gh)):
        x0,y0,t0=s.gh[i-1]; x1,y1,t1=s.gh[i]; age=t-t1; fade=1.0-(age/1.7)
        if fade<=0.02: continue
        c.create_line(x0,y0,x1,y1,fill=g(clamp(40+150*fade,0,215)),width=2)
    x,y=s.pos()
    c.create_polygon(x-24,y-38,x+24,y-38,x+18,y+50,x-18,y+50,fill=g(9),outline=g(28))
    c.create_oval(x-14,y-64,x+14,y-36,fill=g(7),outline=g(24))
    c.create_line(x-26,y-18,x-48,y+8,fill=g(20),width=10,capstyle="round")
    c.create_line(x+26,y-18,x+48,y+8,fill=g(20),width=10,capstyle="round")
    c.create_line(x-10,y+50,x-22,y+92,fill=g(16),width=10,capstyle="round")
    c.create_line(x+10,y+50,x+22,y+92,fill=g(16),width=10,capstyle="round")
    pulse=0.5+0.5*math.sin(t*1.2); c.create_oval(x-16,y-10,x+16,y+22,outline=g(clamp(90+90*pulse,60,190)),width=2)
    for w in s.w:
      fade=1.0-(w["t"]/w["life"]); v=clamp(70+160*fade,60,215); r=w["r"]
      c.create_oval(w["x"]-r,w["y"]-r*0.65,w["x"]+r,w["y"]+r*0.65,outline=g(v),width=2)
    glow=0.3+0.7*(0.5+0.5*math.sin(t*0.85)); c.create_rectangle(0,H-28,W,H,fill=g(clamp(12+55*glow,8,70)),outline="")
    a=s.ha
    def sc(v): return g(clamp(v*(0.25+0.75*a),0,255))
    c.create_text(18,18,anchor="nw",text=f"HOLY DIVER — idle | depth={int(s.d)}",fill=sc(220),font=("Courier",16,"bold"))
    c.create_text(18,44,anchor="nw",text="SPACE/ENTER/Z/X/C=hit • H=hush HUD • R=reset",fill=sc(175),font=("Courier",11))
    c.create_text(18,H-18,anchor="sw",text="THE BOOK WILL LIVE",fill=sc(205),font=("Courier",12,"bold"))
if __name__=="__main__":
  r=tk.Tk(); Idle(r); r.mainloop()
