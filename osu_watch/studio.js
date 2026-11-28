'use strict';
const $=id=>document.getElementById(id);
let camera=null,screen=null,microphone=null,audio=null,output=null,canvasStream=null;
let systemAudioEnabled=false;
let scene='camera',broadcastId=null,viewerPoll=null,inboxPoll=null,drawHandle=null,meterHandle=null;
const peers=new Map();
const canvas=$('program'),ctx=canvas.getContext('2d');
function status(message){$('status').textContent=message}
function stopTracks(stream){if(stream)stream.getTracks().forEach(t=>t.stop())}
function quality(){const q=$('quality').value;return {width:q==='720'?1280:1920,height:q==='720'?720:1080,fps:q==='1080-60'?60:30}}
async function devices(){
 const list=await navigator.mediaDevices.enumerateDevices();
 for(const [id,kind] of [['cameraDevice','videoinput'],['micDevice','audioinput']]){
  const sel=$(id),chosen=sel.value;
  sel.replaceChildren(new Option('System default',''));
  list.filter(d=>d.kind===kind).forEach(d=>sel.add(new Option(d.label||kind,d.deviceId)));
  sel.value=Array.from(sel.options).some(o=>o.value===chosen)?chosen:'';
 }
}
async function captureCamera(){
 stopTracks(camera);
 const q=quality();
 camera=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:q.width},height:{ideal:q.height},frameRate:{ideal:q.fps},...($('cameraDevice').value?{deviceId:{exact:$('cameraDevice').value}}:{})},audio:false});
 $('cameraPreview').srcObject=camera;await $('cameraPreview').play();await devices();
 camera.getVideoTracks()[0].addEventListener('ended',()=>{camera=null;status('Camera disconnected')},{once:true});
}
async function captureMic(){
 stopTracks(microphone);
 microphone=await navigator.mediaDevices.getUserMedia({video:false,audio:{sampleRate:{ideal:48000},channelCount:{ideal:2},echoCancellation:true,noiseSuppression:true,...($('micDevice').value?{deviceId:{exact:$('micDevice').value}}:{})}});
 await devices();
 if(audio)await audio.context.close();
 const context=new AudioContext({sampleRate:48000});await context.resume();
 const source=context.createMediaStreamSource(microphone);
 const gain=context.createGain(),compressor=context.createDynamicsCompressor(),limiter=context.createDynamicsCompressor(),analyser=context.createAnalyser(),destination=context.createMediaStreamDestination();
 compressor.threshold.value=-24;compressor.ratio.value=3;compressor.attack.value=.003;compressor.release.value=.2;
 limiter.threshold.value=-3;limiter.ratio.value=20;limiter.attack.value=.001;limiter.release.value=.08;
 analyser.fftSize=1024;
 source.connect(gain);gain.connect(compressor);compressor.connect(limiter);limiter.connect(analyser);analyser.connect(destination);
 audio={context,gain,compressor,analyser,destination,systemSource:null};
 updateMixer();meter();
}
function updateMixer(){
 if(!audio)return;
 audio.gain.gain.value=$('muteMic').checked?0:1;
}
function clearSystemAudio(){
 if(audio?.systemSource){audio.systemSource.disconnect();audio.systemSource=null}
}
function mixSystemAudio(){
 clearSystemAudio();
 if(!systemAudioEnabled||!screen||!audio||!screen.getAudioTracks().length)return false;
 audio.systemSource=audio.context.createMediaStreamSource(screen);
 audio.systemSource.connect(audio.compressor);
 return true;
}
function meter(){
 if(!audio)return;
 const data=new Float32Array(audio.analyser.fftSize);
 audio.analyser.getFloatTimeDomainData(data);
 const rms=Math.sqrt(data.reduce((sum,v)=>sum+v*v,0)/data.length);
 $('level').value=Math.min(1,rms*3);
 meterHandle=requestAnimationFrame(meter);
}
async function captureScreen(){
 stopTracks(screen);
 clearSystemAudio();
 screen=await navigator.mediaDevices.getDisplayMedia({video:{frameRate:{ideal:quality().fps}},audio:systemAudioEnabled});
 $('screenPreview').srcObject=screen;await $('screenPreview').play();
  if(systemAudioEnabled&&!mixSystemAudio())status('Screen captured — choose “Share audio” to include system sound');
  else if(systemAudioEnabled)status('Screen and system audio ready');
 screen.getVideoTracks()[0].addEventListener('ended',()=>{screen=null;if(scene!=='camera')scene='camera';status('Screen sharing stopped')},{once:true});
}
function drawVideo(video,x,y,w,h){
 if(video.readyState<2)return;
 const sw=video.videoWidth,sh=video.videoHeight;if(!sw||!sh)return;
 const scale=Math.min(w/sw,h/sh),dw=sw*scale,dh=sh*scale;
 ctx.drawImage(video,x+(w-dw)/2,y+(h-dh)/2,dw,dh);
}
function render(){
 const w=canvas.width,h=canvas.height;
 ctx.fillStyle='#080c1a';ctx.fillRect(0,0,w,h);
 if(scene==='slate'){
  ctx.fillStyle='#79e3fa';ctx.textAlign='center';ctx.font='bold '+Math.round(w/16)+'px system-ui';ctx.fillText('APPIE // SIMULATION',w/2,h/2);
  ctx.font=Math.round(w/38)+'px monospace';ctx.fillText('THE SHOW MUST GO ON',w/2,h*.59);ctx.textAlign='left';
 }else{
  const main=scene==='screen'||scene==='pip'&&screen?$('screenPreview'):$('cameraPreview');
  drawVideo(main,0,0,w,h);
  if(scene==='pip'&&camera&&screen){
   const pw=w*.28,ph=h*.28;ctx.fillStyle='#ffffff';ctx.fillRect(w-pw-28,h-ph-28,pw+8,ph+8);
   ctx.fillStyle='#000';ctx.fillRect(w-pw-24,h-ph-24,pw,ph);drawVideo($('cameraPreview'),w-pw-24,h-ph-24,pw,ph);
  }
 }
 if($('overlay').checked){
  ctx.fillStyle='rgba(7,12,28,.8)';ctx.fillRect(0,h*.85,w,h*.15);
  ctx.fillStyle='white';ctx.font='bold '+Math.round(w/31)+'px system-ui';ctx.fillText($('title').value.slice(0,80),w*.04,h*.94);
 }
 drawHandle=requestAnimationFrame(render);
}
function streamOutput(){
 const q=quality();canvas.width=q.width;canvas.height=q.height;
 canvasStream=canvas.captureStream(q.fps);
 const tracks=[...canvasStream.getVideoTracks(),...audio.destination.stream.getAudioTracks()];
 output=new MediaStream(tracks);
}
async function api(path,options={}){
 const response=await fetch(path,{cache:'no-store',...options});
 const result=await response.json();if(!response.ok)throw Error(result.error||'HTTP '+response.status);
 return result;
}
async function post(path,data,token=false){
 return api(path,{method:'POST',headers:{'Content-Type':'application/json',...(token?{'X-Studio-Token':$('token').value}:{})},body:JSON.stringify(data)});
}
async function waitIce(pc){
 if(pc.iceGatheringState==='complete')return;
 await new Promise(resolve=>{const timer=setTimeout(resolve,4000);pc.addEventListener('icegatheringstatechange',function done(){if(pc.iceGatheringState==='complete'){clearTimeout(timer);pc.removeEventListener('icegatheringstatechange',done);resolve()} })});
}
async function addViewer(id){
 if(peers.has(id)||!broadcastId)return;
 const pc=new RTCPeerConnection({iceServers:[]});peers.set(id,pc);
 output.getTracks().forEach(track=>pc.addTrack(track,output));
 pc.onconnectionstatechange=()=>{if(['closed','failed','disconnected'].includes(pc.connectionState)){pc.close();peers.delete(id)}};
 try{
  await pc.setLocalDescription(await pc.createOffer());await waitIce(pc);
  await post('/api/live/send',{from:broadcastId,to:id,type:'offer',payload:pc.localDescription});
 }catch(e){pc.close();peers.delete(id);status('Viewer connection error: '+e.message)}
}
async function poll(){
 if(!broadcastId)return;
 try{
  const viewers=await api('/api/live/viewers?id='+encodeURIComponent(broadcastId));
  for(const id of viewers.viewers)await addViewer(id);
  $('viewers').textContent=peers.size+' connected/connecting viewers';
 }catch(e){status('Broadcast session error: '+e.message);await stopBroadcast()}
}
async function inbox(){
 if(!broadcastId)return;
 try{
  const result=await api('/api/live/inbox?id='+encodeURIComponent(broadcastId));
  for(const msg of result.messages){
   const pc=peers.get(msg.from);
   if(msg.type==='answer'&&pc&&pc.signalingState==='have-local-offer')await pc.setRemoteDescription(msg.payload);
  }
 }catch(e){status('Signaling error: '+e.message)}
}
async function prepare(){
 $('prepare').disabled=true;status('Preparing devices…');
 try{
  if(!navigator.mediaDevices||!canvas.captureStream)throw Error('Secure browser context and canvas capture required');
  systemAudioEnabled=$('systemAudio').checked;
  await captureCamera();await captureMic();
  if(screen&&systemAudioEnabled)mixSystemAudio();
  streamOutput();
  if(!drawHandle)render();
  $('go').disabled=false;status('READY — preview only, not broadcasting');
  const v=camera.getVideoTracks()[0].getSettings();
  $('stats').textContent='Camera '+(v.width||'?')+'×'+(v.height||'?')+' @ '+(v.frameRate||'?')+' fps';
 }catch(e){status('Preparation failed: '+e.message);$('prepare').disabled=false;await releaseMedia()}
}
async function goLive(){
 if(!output)return;
 $('go').disabled=true;status('Connecting…');
 try{
  const reg=await post('/api/live/register',{role:'broadcaster'},true);broadcastId=reg.id;
  $('stop').disabled=false;status('ON AIR');
  viewerPoll=setInterval(poll,1000);inboxPoll=setInterval(inbox,500);
  await poll();await inbox();
 }catch(e){status('Could not go live: '+e.message);$('go').disabled=false}
}
async function stopBroadcast(){
 clearInterval(viewerPoll);clearInterval(inboxPoll);viewerPoll=inboxPoll=null;
 peers.forEach(pc=>pc.close());peers.clear();
 const id=broadcastId;broadcastId=null;
 if(id)try{await post('/api/live/leave',{id})}catch{}
 $('go').disabled=!output;$('stop').disabled=true;status('OFF AIR — preview remains ready');
}
async function releaseMedia(){
 clearSystemAudio();stopTracks(camera);stopTracks(screen);stopTracks(microphone);stopTracks(canvasStream);
 camera=screen=microphone=canvasStream=output=null;
 cancelAnimationFrame(meterHandle);cancelAnimationFrame(drawHandle);meterHandle=drawHandle=null;
 if(audio){await audio.context.close();audio=null}
}
$('prepare').onclick=prepare;$('go').onclick=goLive;$('stop').onclick=stopBroadcast;
$('systemAudio').onchange=()=>{systemAudioEnabled=$('systemAudio').checked;if(screen){status('Re-share the screen to change system audio') }};
$('camera').onclick=async()=>{try{if(!camera)await captureCamera();scene='camera'}catch(e){status(e.message)}};
$('screen').onclick=async()=>{try{if(!screen)await captureScreen();scene='screen'}catch(e){status(e.message)}};
$('pip').onclick=async()=>{try{if(!screen)await captureScreen();if(!camera)await captureCamera();scene='pip'}catch(e){status(e.message)}};
$('slate').onclick=()=>{scene='slate'};
$('muteMic').oninput=updateMixer;
$('quality').onchange=()=>{if(output)status('Quality change requires refreshing and preparing studio again')};
window.addEventListener('pagehide',()=>{clearInterval(viewerPoll);clearInterval(inboxPoll);peers.forEach(pc=>pc.close());stopTracks(camera);stopTracks(screen);stopTracks(microphone);stopTracks(canvasStream)});
if(navigator.mediaDevices)devices().catch(()=>{});
