function load(buffer){
let notes=parseMidi(buffer);
midiToBeatmap(notes);
console.log("beatmap ready:",Beatmap.objects.length);
}

addEventListener("keydown",async()=>{
if(!window.started){
window.started=true;
if(AudioCtx) await AudioCtx.resume();
loop("osu");
}
});
