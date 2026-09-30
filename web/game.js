let currentMode = null;
let audio = new Audio("../mix_assets/audio/mix_track.mp3");
audio.loop = true;

function startMode(mode) {
    currentMode = mode;
    document.getElementById('menu').style.display = 'none';
    document.getElementById('gameCanvas').style.display = 'block';
    if (audio.paused) audio.play();
    gameLoop();
}

function bustToMegamix() {
    alert("You busted to the Megamix!");
    // Optional: reset health, keep timeline going
}

function gameLoop() {
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    
    ctx.clearRect(0,0,canvas.width,canvas.height);
    
    // Draw gameplay elements here
    ctx.fillStyle = "#f00";
    ctx.fillRect(Math.random()*canvas.width, Math.random()*canvas.height, 50, 50);

    // Random fail simulation (for demo)
    if (Math.random() < 0.001 && currentMode === 'mix') bustToMegamix();

    requestAnimationFrame(gameLoop);
}

