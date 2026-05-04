window.MidiPlayer={i:0,started:false};

function startMidi(){
MidiPlayer.started=true;

function loop(){
let t=Stream.beat(120);
let n=MidiStream.notes;

while(MidiPlayer.i<n.length && n[MidiPlayer.i].t<=t){

let e=n[MidiPlayer.i];

let type =
e.note<40?"bass":
e.note<60?"drum":
e.note<80?"piano":"synth";

play(type,e.note,0);

MidiPlayer.i++;
}

requestAnimationFrame(loop);
}

loop();
}
