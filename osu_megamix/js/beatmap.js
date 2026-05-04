window.Beatmap={objects:[]};

function midiToBeatmap(notes){
Beatmap.objects=notes.map(n=>({
t:n.t*1000,
lane:n.note%4,
note:n.note
}));
return Beatmap.objects;
}
