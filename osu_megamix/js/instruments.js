window.AudioCtx=new (window.AudioContext||window.webkitAudioContext)();

function freq(n){return 440*Math.pow(2,(n-69)/12);}

function play(type,n,t){
let o=AudioCtx.createOscillator();
let g=AudioCtx.createGain();

if(type==="bass"){o.type="sawtooth";g.gain.value=0.05}
if(type==="piano"){o.type="triangle";g.gain.value=0.04}
if(type==="synth"){o.type="square";g.gain.value=0.03}
if(type==="drum"){o.type="sine";g.gain.value=0.08}

let f=freq(n);
if(type==="bass") f*=0.5;
if(type==="drum") f=120;

o.frequency.value=f;

o.connect(g);
g.connect(AudioCtx.destination);

o.start(AudioCtx.currentTime+t);
o.stop(AudioCtx.currentTime+t+0.2);
}
