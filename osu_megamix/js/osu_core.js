function judge(dt){
let a=Math.abs(dt);
if(a<30)return 300;
if(a<70)return 100;
if(a<110)return 50;
return 0;
}
