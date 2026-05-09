export const mix = {

  canvas:null,
  ctx:null,

  time:0,
  delta:0,
  last:0,

  score:0,
  combo:0,
  hp:100,

  density:1,
  busted:false,

  notes:[],
  pool:[],

  chart:[],
  chartIndex:0,

  rulesets:{},
  systems:{},

  camera:{
    x:0,
    y:0,
    shake:0,
    zoom:1
  },

  mouse:{
    x:0,
    y:0,
    down:false
  },

  keys:{}
};

export function boot(){

  mix.canvas =
    document.getElementById('game');

  mix.ctx =
    mix.canvas.getContext('2d');

  resize();

  addEventListener(
    'resize',
    resize
  );

  requestAnimationFrame(loop);
}

function resize(){

  mix.canvas.width = innerWidth;
  mix.canvas.height = innerHeight;
}

function loop(t){

  mix.delta = t - mix.last;
  mix.last = t;
  mix.time = t;

  updateSystems();
  render();

  requestAnimationFrame(loop);
}

function updateSystems(){

  Object.values(
    mix.systems
  ).forEach(fn=>fn());
}

function render(){

  const ctx = mix.ctx;
  const cam = mix.camera;

  cam.shake *= .9;

  ctx.setTransform(
    cam.zoom,
    0,
    0,
    cam.zoom,
    (Math.random()-.5)*cam.shake,
    (Math.random()-.5)*cam.shake
  );

  ctx.fillStyle =
    mix.busted
    ? 'rgba(30,0,0,.25)'
    : 'rgba(0,0,0,.2)';

  ctx.fillRect(
    -100,
    -100,
    mix.canvas.width+200,
    mix.canvas.height+200
  );

  for(const n of mix.notes){

    if(n.hit) continue;

    const rs =
      mix.rulesets[n.ruleset];

    if(rs){
      rs.update(n);
      rs.render(n);
    }
  }

  mix.notes = mix.notes.filter(n=>{

    if(n.hit){

      mix.pool.push(n);

      return false;
    }

    return true;
  });
}
