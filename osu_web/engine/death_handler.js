export function triggerDeath(score){
  if(score.health <= 0){
    alert("Player died! Returning to Megamix title...");
    document.getElementById('menu').style.display='block';
    return true;
  }
  return false;
}
