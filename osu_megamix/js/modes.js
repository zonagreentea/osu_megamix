window.mode = 0;

window.setMode = function(m){
  mode = m;
  console.log("mode:", ["osu","taiko","catch","mania"][m]);
};

window.getModeName = () =>
  ["osu","taiko","catch","mania"][mode];
