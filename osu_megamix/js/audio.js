window.AudioCtx = new (window.AudioContext || window.webkitAudioContext)();

window.Stream = {
  start: performance.now(),
  time(){ return performance.now() - this.start },
  beat(bpm=120){ return this.time() / (60000/bpm) }
};

window.AudioStream = {
  bpm: 120,
  next: 0
};

function beep(f=220,t=0){
  let o=AudioCtx.createOscillator();
  let g=AudioCtx.createGain();

  o.type="square";
  o.frequency.value=f;
  g.gain.value=0.03;

  o.connect(g);
  g.connect(AudioCtx.destination);

  o.start(AudioCtx.currentTime+t);
  o.stop(AudioCtx.currentTime+t+0.06);
}

function startStream(){

function loop(){
  let b = Stream.beat(AudioStream.bpm);

  if(b >= AudioStream.next){
    beep(220 + (AudioStream.next%4)*70);
    if(AudioStream.next % 2 === 0) beep(440);
    AudioStream.next++;
  }

  requestAnimationFrame(loop);
}

loop();
}

addEventListener("keydown", async ()=>{
  if(AudioCtx.state !== "running"){
    await AudioCtx.resume();
    startStream();
  }
});
