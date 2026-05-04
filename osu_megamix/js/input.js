window.keys = {};

addEventListener("keydown", e=>{
  keys[e.key.toLowerCase()] = true;

  if(e.key==="1") setMode(0);
  if(e.key==="2") setMode(1);
  if(e.key==="3") setMode(2);
  if(e.key==="4") setMode(3);
});

addEventListener("keyup", e=>{
  keys[e.key.toLowerCase()] = false;
});
