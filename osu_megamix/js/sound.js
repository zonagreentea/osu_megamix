window.AudioCtx=new (window.AudioContext||window.webkitAudioContext)();

function tick(){
let o=AudioCtx.createOscillator();
let g=AudioCtx.createGain();

o.frequency.value=800;
g.gain.value=0.03;

o.connect(g);
g.connect(AudioCtx.destination);

o.start();
o.stop(AudioCtx.currentTime+0.05);
}
