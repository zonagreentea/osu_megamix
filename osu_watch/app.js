'use strict';
let stream = null;
const $ = id => document.getElementById(id);
async function loadChannel(){
  if (!$('state')) return;
  try {
    const response = await fetch('/api/channel', {cache:'no-store'});
    if (!response.ok) throw new Error('Channel unavailable');
    const channel = await response.json();
    $('state').textContent = channel.live ? 'Live now' : 'Channel ready — standby';
    $('schedule').replaceChildren(...channel.schedule.map(item => {
      const row = document.createElement('div'); row.className = 'schedule-item';
      row.textContent = `${item.title} · ${item.status}`; return row;
    }));
  } catch { $('state').textContent = 'Channel offline'; }
}
async function startPreview(){
  if (!navigator.mediaDevices?.getUserMedia) { $('permission').textContent = 'Media access requires localhost or HTTPS and a supported browser.'; return; }
  try {
    stopPreview();
    stream = await navigator.mediaDevices.getUserMedia({video:true,audio:true});
    $('preview').srcObject = stream;
    $('permission').textContent = 'Local preview active';
    $('audio').textContent = 'Microphone connected (local preview only)';
  } catch (error) { $('permission').textContent = `Permission or device error: ${error.name}`; }
}
function stopPreview(){
  if (stream) stream.getTracks().forEach(track => track.stop());
  stream = null;
  if ($('preview')) $('preview').srcObject = null;
  if ($('permission')) $('permission').textContent = 'Camera and microphone are off.';
  if ($('audio')) $('audio').textContent = 'Microphone disconnected';
}
$('camera')?.addEventListener('click', startPreview);
$('stop')?.addEventListener('click', stopPreview);
window.addEventListener('pagehide', stopPreview);
loadChannel();
