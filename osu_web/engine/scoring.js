export class Score {
  constructor(){ this.combo=0; this.points=0; this.health=100; }
  hit(value=300){ this.combo++; this.points+=value; this.health=Math.min(100,this.health+2); }
  miss(penalty=10){ this.combo=0; this.health-=penalty; }
  reset(){ this.combo=0; this.points=0; this.health=100; }
}
