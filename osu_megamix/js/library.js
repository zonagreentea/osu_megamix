window.MegamixLibrary = {
  songs: []
};

function registerSong(song){
  MegamixLibrary.songs.push(song);
}

function getSong(i=0){
  return MegamixLibrary.songs[i];
}
