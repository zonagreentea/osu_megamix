from pathlib import Path
import shutil
root=Path.cwd()
html=root/'games/tetris_ltm/index.html'
if not html.exists(): raise SystemExit('Run from the osu_megamix repository root')
source=Path(__file__).resolve().parent/'osu_tetris_voicelines.m4a'
dest=root/'games/tetris_ltm/audio/osu_tetris_voicelines.m4a'
dest.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(source,dest)
s=html.read_text()
if 'const VOICE_CUES=' in s: raise SystemExit('Audio copied; voice integration already installed')
start=s.index('let subtitleTimer=0;')
end=s.index("$('subtitle-mode').addEventListener",start)
replacement='''// Recording contains more phrases than gameplay events. Adjust these cue boundaries after listening.
// These are preliminary timestamps detected from pauses in the supplied 49.37-second recording.
const VOICE_CUES={
  single:[17.25,18.23],
  double:[20.66,21.28],
  triple:[24.10,24.94],
  tetris:[27.27,28.35],
  over:[31.07,31.35]
};
const voiceAudio=new Audio('./audio/osu_tetris_voicelines.m4a');
voiceAudio.preload='auto';
let subtitleTimer=0,voiceTimer=0;
function clearVoice(){
  clearTimeout(subtitleTimer);
  clearTimeout(voiceTimer);
  $('subtitle').textContent='';
  voiceAudio.pause();
}
function sayRussian(key){
  if(!eventActive()||key==='start')return;
  const line=VOICE_LINES[key],cue=VOICE_CUES[key];
  if(!line||!cue)return;
  clearVoice();
  const subtitleMode=$('subtitle-mode').value;
  if(subtitleMode!=='off')$('subtitle').textContent=subtitleMode==='ru'?line[0]:line[1];
  subtitleTimer=setTimeout(()=>$('subtitle').textContent='',2600);
  if(!$('voices-enabled').checked)return;
  voiceAudio.currentTime=cue[0];
  voiceAudio.play().then(()=>{
    voiceTimer=setTimeout(()=>voiceAudio.pause(),Math.max(0,(cue[1]-cue[0])*1000));
  }).catch(err=>console.warn('Voice playback unavailable:',err));
}
$('voices-enabled').addEventListener('change',()=>{if(!$('voices-enabled').checked)clearVoice()});
'''
s=s[:start]+replacement+s[end:]
s=s.replace("newPiece();sayRussian('start')}","newPiece()}")
html.write_text(s)
print('Installed voice audio and patched',html)
print('Review VOICE_CUES timestamps before release.')
