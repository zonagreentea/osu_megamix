window.MidiStream={notes:[]};

function parseMidi(buffer){
let dv=new DataView(buffer);
let notes=[];
for(let i=0;i<dv.byteLength-3;i++){
if(dv.getUint8(i)===0x90){
let n=dv.getUint8(i+1);
let v=dv.getUint8(i+2);
if(v>0) notes.push({t:notes.length*0.5,note:n,vel:v});
}
}
MidiStream.notes=notes;
return notes;
}
