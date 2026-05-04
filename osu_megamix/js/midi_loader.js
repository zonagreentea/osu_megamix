async function loadMidi(path){
  const res = await fetch(path);
  const buffer = await res.arrayBuffer();
  return buffer; // placeholder for parser
}

window.loadMidi = loadMidi;
