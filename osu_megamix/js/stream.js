window.Stream={
start:performance.now(),
time(){return performance.now()-this.start},
beat(bpm=120){return this.time()/(60000/bpm)}
};
