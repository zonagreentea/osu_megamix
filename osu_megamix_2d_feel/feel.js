(()=>{'use strict';
const $=id=>document.getElementById(id),canvas=$('field'),ctx=canvas.getContext('2d',{alpha:false});
const W=960,H=540,TAU=Math.PI*2,colors=['#ff70b9','#7aefff','#f9d86e','#a68bff'];
let mode='osu',phase='ready',objects=[],particles=[],score=0,combo=0,maxCombo=0,health=100,hits=0,weight=0,judged=0,time=0,last=0,next=0,duration=60000,raf=0,pointer={x:480,y:270},keys=new Set(),muted=false,audio=null,modeCycle=0;
const rand=(a,b)=>a+Math.random()*(b-a),clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
function sound(freq=500){if(muted)return;try{audio??=new (window.AudioContext||window.webkitAudioContext)();if(audio.state==='suspended')audio.resume();const o=audio.createOscillator(),g=audio.createGain(),t=audio.currentTime;o.type='sine';o.frequency.setValueAtTime(freq,t);o.frequency.exponentialRampToValueAtTime(freq*.6,t+.075);g.gain.setValueAtTime(.07,t);g.gain.exponentialRampToValueAtTime(.001,t+.095);o.connect(g).connect(audio.destination);o.start(t);o.stop(t+.1)}catch{}}
function hud(){ $('score').textContent=String(score).padStart(8,'0');$('combo').textContent=combo+'×';$('accuracy').textContent=(judged?100*weight/judged:100).toFixed(2)+'%';$('health').style.width=health+'%';}
function overlay(tag,title,desc,action){$('overlayTag').textContent=tag;$('overlayTitle').textContent=title;$('overlayDesc').textContent=desc;$('play').textContent=action;$('overlay').classList.remove('hidden')}
function controls(){return {osu:'Move with pointer • Z / X / click to hit',taiko:'D / F = red • J / K = blue',catch:'Move pointer or ← / → to catch fruit',mania:'D / F / J / K for four lanes',megamix:'Mixed osu! and Mania • Z / X / click + D / F / J / K'}[mode]}
function choose(m){mode=m;document.querySelectorAll('[data-mode]').forEach(b=>b.classList.toggle('active',b.dataset.mode===m));reset();$('controls').textContent=controls();overlay('SELECTED MODE',m.toUpperCase()+' — FEEL','60 seconds of playable rhythm action. '+controls(),'▶ START PLAYING')}
function reset(){cancelAnimationFrame(raf);phase='ready';objects=[];particles=[];score=combo=maxCombo=hits=weight=judged=time=next=modeCycle=0;health=100;keys.clear();$('feedback').textContent='READY';$('status').textContent='READY';hud();draw()}
function start(){if(phase==='paused'){phase='playing';last=performance.now();$('overlay').classList.add('hidden');raf=requestAnimationFrame(loop);return}reset();phase='playing';$('status').textContent='LIVE';$('overlay').classList.add('hidden');last=performance.now();raf=requestAnimationFrame(loop)}
function pause(){if(phase==='playing'){phase='paused';cancelAnimationFrame(raf);$('status').textContent='PAUSED';overlay('TAKE A MOMENT','PAUSED','Your run is waiting.','▶ RESUME')}else if(phase==='paused')start()}
function finish(){phase='finished';cancelAnimationFrame(raf);$('status').textContent='FINISHED';overlay('RUN COMPLETE',health<=0?'GAME OVER':'NICE PLAY!',`Score ${score.toLocaleString()} • Max combo ${maxCombo} • Accuracy ${(judged?100*weight/judged:100).toFixed(2)}%`,'↻ PLAY AGAIN')}
function type(){if(mode==='megamix')return modeCycle++%3===0?'mania':'osu';return mode}
function spawn(){const kind=type(),lane=Math.floor(rand(0,4)),color=kind==='taiko'?Math.floor(rand(0,2)):lane;const obj={kind,lane,color,born:time,hitAt:time+1550,dead:false,id:Math.random(),x:rand(100,860),y:rand(90,420)};if(kind==='osu')obj.hitAt=time+1200;if(kind==='catch'){obj.x=rand(80,880);obj.hitAt=time+1700}objects.push(obj)}
function burst(x,y,c){for(let i=0;i<11;i++)particles.push({x,y,vx:rand(-140,140),vy:rand(-150,80),life:.4,color:c})}
function judge(o,delta){if(o.dead)return;o.dead=true;judged++;const a=Math.abs(delta);const grade=a<=55?1:a<=110?.7:a<=170?.3:0;if(grade){hits++;combo++;maxCombo=Math.max(maxCombo,combo);weight+=grade;score+=Math.round((grade===1?300:grade===.7?100:50)*(1+Math.min(combo,100)/25));health=clamp(health+2,0,100);$('feedback').textContent=grade===1?'PERFECT ✦':grade===.7?'GREAT':'GOOD';sound(460+combo%10*34);burst(o.kind==='mania'?330+o.lane*100:o.kind==='taiko'?310:o.x,o.kind==='mania'?440:o.kind==='taiko'?270:o.y,colors[o.color%4])}else{combo=0;health=clamp(health-8,0,100);$('feedback').textContent='MISS'}hud()}
function hit(kind,lane=-1){if(phase!=='playing')return;const candidates=objects.filter(o=>!o.dead&&o.kind===kind&&(lane<0||o.lane===lane)&&Math.abs(time-o.hitAt)<175);if(kind==='osu')candidates.sort((a,b)=>Math.hypot(a.x-pointer.x,a.y-pointer.y)-Math.hypot(b.x-pointer.x,b.y-pointer.y));else candidates.sort((a,b)=>Math.abs(time-a.hitAt)-Math.abs(time-b.hitAt));const o=candidates[0];if(!o)return;if(kind==='osu'&&Math.hypot(o.x-pointer.x,o.y-pointer.y)>85)return;judge(o,time-o.hitAt)}
function input(code){if(code==='Escape'||code==='Space'){pause();return}if(code==='KeyR'){start();return}if(phase!=='playing')return;const lane={KeyD:0,KeyF:1,KeyJ:2,KeyK:3}[code];if(lane!==undefined){hit('mania',lane);if(code==='KeyD'||code==='KeyF')hit('taiko',0);else hit('taiko',1)}if(code==='KeyZ'||code==='KeyX')hit('osu')}
function loop(now){if(phase!=='playing')return;const dt=clamp((now-last)/1000,0,.05);last=now;time+=dt*1000;const interval=mode==='mania'?390:mode==='megamix'?470:mode==='catch'?520:570;while(time>=next&&next<duration-1800){spawn();next+=interval}for(const o of objects){if(!o.dead&&time>o.hitAt+(o.kind==='catch'?100:180)){if(o.kind==='catch'){const catcher=pointer.x;if(Math.abs(catcher-o.x)<78)judge(o,0);else judge(o,999)}else judge(o,999)}}objects=objects.filter(o=>!o.dead&&time-o.hitAt<500);particles.forEach(p=>{p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=260*dt;p.life-=dt});particles=particles.filter(p=>p.life>0);if(keys.has('ArrowLeft')||keys.has('KeyA'))pointer.x=clamp(pointer.x-560*dt,50,910);if(keys.has('ArrowRight')||keys.has('KeyL'))pointer.x=clamp(pointer.x+560*dt,50,910);if(health<=0||time>=duration){finish();draw();return}draw();raf=requestAnimationFrame(loop)}
function circle(x,y,r,c,fill=true,line=4){ctx.beginPath();ctx.arc(x,y,Math.max(1,r),0,TAU);if(fill){ctx.fillStyle=c;ctx.fill()}else{ctx.strokeStyle=c;ctx.lineWidth=line;ctx.stroke()}}
function rect(x,y,w,h,c){ctx.fillStyle=c;ctx.fillRect(x,y,w,h)}
function draw(){
 const box=canvas.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2);
 const bw=Math.max(1,Math.round(box.width*dpr)),bh=Math.max(1,Math.round(box.height*dpr));
 if(canvas.width!==bw||canvas.height!==bh){canvas.width=bw;canvas.height=bh}
 ctx.setTransform(bw/W,0,0,bh/H,0,0);
 const t=performance.now()*.001;
 const bg=ctx.createLinearGradient(0,0,W,H);
 bg.addColorStop(0,'#090e24');bg.addColorStop(.55,'#15102d');bg.addColorStop(1,'#061c29');
 rect(0,0,W,H,bg);
 const aura=ctx.createRadialGradient(480+Math.sin(t*.3)*130,260,10,480,270,580);
 aura.addColorStop(0,'#8045b022');aura.addColorStop(.5,'#1d92c012');aura.addColorStop(1,'#00000000');
 rect(0,0,W,H,aura);
 ctx.save();
 for(let i=0;i<78;i++){
  const x=(i*173.31+37)%W,y=(i*97.17+13)%H;
  const a=.1+.32*(.5+.5*Math.sin(t*(.5+i%4*.2)+i*2.7));
  ctx.globalAlpha=a;circle(x,y,i%9===0?2.2:1.1,i%3===0?'#90efff':'#ffffff');
 }
 ctx.globalAlpha=1;
 ctx.strokeStyle='#b5c9ff0b';ctx.lineWidth=1;
 const offset=(time*.012)%48;
 for(let x=-48+offset;x<W;x+=48){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke()}
 for(let y=-48+offset;y<H;y+=48){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke()}
 ctx.restore();
 ctx.save();ctx.textAlign='center';ctx.font='800 12px system-ui';ctx.letterSpacing='3px';
 ctx.fillStyle='#ffffff44';ctx.fillText('FEEL / '+mode.toUpperCase(),480,28);ctx.restore();
 if(mode==='mania'||mode==='megamix'){
  ctx.save();ctx.shadowColor='#9c6dff';ctx.shadowBlur=25;
  const g=ctx.createLinearGradient(0,40,0,490);g.addColorStop(0,'#292347aa');g.addColorStop(1,'#1c2e4aaa');
  rect(280,40,400,450,g);ctx.restore();
  for(let i=0;i<4;i++){
   rect(280+i*100,40,2,450,'#ffffff25');
   const laneGlow=ctx.createLinearGradient(0,410,0,470);
   laneGlow.addColorStop(0,'#00000000');laneGlow.addColorStop(1,colors[i]+'55');
   rect(285+i*100,400,90,70,laneGlow);
   ctx.save();ctx.shadowColor=colors[i];ctx.shadowBlur=22;rect(287+i*100,434,86,6,colors[i]);ctx.restore();
  }
 }
 if(mode==='taiko'){
  const rail=ctx.createLinearGradient(0,225,0,320);
  rail.addColorStop(0,'#423251cc');rail.addColorStop(.5,'#24223c');rail.addColorStop(1,'#0e1934');
  rect(90,225,780,95,rail);
  ctx.save();ctx.shadowColor='#ffe5ff';ctx.shadowBlur=26;circle(310,272,47,'#ffffff',false,5);ctx.restore();
  circle(310,272,34,'#ff7cb855',false,4);
 }
 if(mode==='catch'){
  const floor=ctx.createLinearGradient(0,455,0,540);floor.addColorStop(0,'#19486a55');floor.addColorStop(1,'#071527');
  rect(0,455,W,85,floor);
  ctx.save();ctx.shadowColor='#79f5ff';ctx.shadowBlur=28;
  const basket=ctx.createLinearGradient(pointer.x-68,0,pointer.x+68,0);
  basket.addColorStop(0,'#74eaff');basket.addColorStop(.5,'#ffffff');basket.addColorStop(1,'#e78aff');
  rect(pointer.x-68,462,136,12,basket);ctx.restore();
 }
 for(const o of objects){
  if(o.dead)continue;
  const remaining=o.hitAt-time,c=colors[o.color%4];
  if(o.kind==='osu'){
   const progress=clamp(remaining/1200,0,1),r=45;
   ctx.save();ctx.shadowColor=c;ctx.shadowBlur=35;
   const orb=ctx.createRadialGradient(o.x-12,o.y-15,2,o.x,o.y,r);
   orb.addColorStop(0,'#ffffff');orb.addColorStop(.22,c);orb.addColorStop(1,'#211e4c');
   circle(o.x,o.y,r,orb);ctx.restore();
   circle(o.x,o.y,r,'#ffffffd9',false,4);
   circle(o.x,o.y,r+progress*95,c+'aa',false,3);
   circle(o.x,o.y,r+progress*95+8,c+'44',false,2);
   circle(o.x-12,o.y-15,8,'#ffffffaa');
  }else if(o.kind==='taiko'){
   const x=310+remaining*.37,cc=o.color===0?'#ff6b9b':'#6beaff';
   ctx.save();ctx.shadowColor=cc;ctx.shadowBlur=26;circle(x,272,36,cc);ctx.restore();
   circle(x-9,262,10,'#ffffff88');circle(x,272,36,'#ffffffcc',false,3);
  }else if(o.kind==='mania'){
   const y=440-remaining*.25,x=290+o.lane*100;
   ctx.save();ctx.shadowColor=c;ctx.shadowBlur=24;
   const note=ctx.createLinearGradient(x,y-16,x,y+10);note.addColorStop(0,'#ffffff');note.addColorStop(.35,c);note.addColorStop(1,'#5142a0');
   rect(x,y-16,80,26,note);ctx.restore();
   rect(x+5,y-12,70,3,'#ffffffbb');
  }else if(o.kind==='catch'){
   const y=470-remaining*.25;
   ctx.save();ctx.shadowColor=c;ctx.shadowBlur=24;circle(o.x,y,21,c);ctx.restore();
   circle(o.x-6,y-6,7,'#ffffffbb');
   circle(o.x,y,21,'#ffffff88',false,2);
  }
 }
 if(mode==='osu'||mode==='megamix'){
  ctx.save();ctx.shadowColor='#83eaff';ctx.shadowBlur=22;
  circle(pointer.x,pointer.y,17,'#ffffff',false,2);
  circle(pointer.x,pointer.y,5,'#77f4ff');
  ctx.restore();
  circle(pointer.x,pointer.y,26,'#77f4ff55',false,1);
 }
 for(const p of particles){
  ctx.globalAlpha=clamp(p.life/.4,0,1);
  ctx.save();ctx.shadowColor=p.color;ctx.shadowBlur=12;
  circle(p.x,p.y,3,p.color);ctx.restore();
 }
 ctx.globalAlpha=1;
 rect(0,H-5,W*clamp(time/duration,0,1),5,'#ff69b7');
 const vignette=ctx.createRadialGradient(W/2,H/2,150,W/2,H/2,630);
 vignette.addColorStop(0,'#00000000');vignette.addColorStop(1,'#00000077');
 rect(0,0,W,H,vignette);
}
function position(e){const r=canvas.getBoundingClientRect();pointer.x=clamp((e.clientX-r.left)/r.width*W,0,W);pointer.y=clamp((e.clientY-r.top)/r.height*H,0,H)}
canvas.addEventListener('pointermove',position);canvas.addEventListener('pointerdown',e=>{position(e);if(phase==='playing'){hit('osu');if(mode==='taiko')hit('taiko',0)}else if(phase==='ready')start()});document.addEventListener('keydown',e=>{if(['Space','ArrowLeft','ArrowRight','Escape'].includes(e.code))e.preventDefault();if(!e.repeat)input(e.code);keys.add(e.code)});document.addEventListener('keyup',e=>keys.delete(e.code));window.addEventListener('blur',()=>{keys.clear();if(phase==='playing')pause()});document.addEventListener('visibilitychange',()=>{if(document.hidden&&phase==='playing')pause()});window.addEventListener('resize',draw);document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>choose(b.dataset.mode)));$('play').addEventListener('click',start);$('pause').addEventListener('click',pause);$('retry').addEventListener('click',start);$('mute').addEventListener('click',()=>{muted=!muted;$('mute').textContent=muted?'♫ Sound off':'♫ Sound on'});$('fullscreen').addEventListener('click',()=>{if(!document.fullscreenElement)$('field').parentElement.requestFullscreen?.();else document.exitFullscreen?.()});choose('osu');
})();
