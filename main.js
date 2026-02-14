const canvas = document.getElementById('petCanvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const pet = {
    x: canvas.width / 2,
    y: canvas.height / 2,
    radius: 25,
    color: '#FF00FF', // subtle flex color
    speed: 5,
    boost: 12,
};

const keys = { left: false, right: false, boost: false };

window.addEventListener('keydown', (e) => {
    if(e.key === 'ArrowLeft' || e.key === 'a') keys.left = true;
    if(e.key === 'ArrowRight' || e.key === 'd') keys.right = true;
    if(e.key === 'Shift') keys.boost = true;
});

window.addEventListener('keyup', (e) => {
    if(e.key === 'ArrowLeft' || e.key === 'a') keys.left = false;
    if(e.key === 'ArrowRight' || e.key === 'd') keys.right = false;
    if(e.key === 'Shift') keys.boost = false;
});

function update() {
    const moveSpeed = keys.boost ? pet.boost : pet.speed;
    if(keys.left) pet.x -= moveSpeed;
    if(keys.right) pet.x += moveSpeed;
    pet.x = Math.max(pet.radius, Math.min(canvas.width - pet.radius, pet.x));
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = pet.color;
    ctx.beginPath();
    ctx.arc(pet.x, pet.y, pet.radius, 0, Math.PI * 2);
    ctx.fill();
}

function loop() {
    update();
    draw();
    requestAnimationFrame(loop);
}

loop();

