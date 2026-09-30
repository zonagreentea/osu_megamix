export function triggerDeath(score){
if(score.health<=0){alert("Player died! Returning to Megamix menu");document.getElementById('menu').style.display='block';return true;}
return false;
}
