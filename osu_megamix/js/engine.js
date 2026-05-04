window.Engine = {
  bpm: 120,
  spb: 0.5,
  start: performance.now(),

  time(){
    return performance.now() - this.start;
  },

  beat(){
    return this.time() / (this.spb * 1000);
  }
};
