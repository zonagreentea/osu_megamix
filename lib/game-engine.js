import { getModeConfig } from './mode-configs.js';
import { createAudioController } from './audio.js';

export class GameEngine {
  constructor({ canvasId, mode = 'osu' }) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.mode = mode;
    this.config = getModeConfig(mode);
    this.state = {
      score: 0,
      combo: 0,
      health: 100,
      objects: [],
      flash: 0,
      spawnAccumulator: 0
    };
    this.keys = {};
    this.lastTime = 0;
    this.audio = createAudioController();
    this.bindInput();
  }

  bindInput() {
    window.addEventListener('keydown', (event) => {
      const key = event.key.toLowerCase();
      this.keys[key] = true;
      this.handleInput(key);
    });

    window.addEventListener('keyup', (event) => {
      this.keys[event.key.toLowerCase()] = false;
    });
  }

  start() {
    this.lastTime = performance.now();
    requestAnimationFrame((timestamp) => this.loop(timestamp));
  }

  loop(timestamp) {
    const dt = (timestamp - this.lastTime) / 1000;
    this.lastTime = timestamp;

    this.update(dt);
    this.render();

    requestAnimationFrame((nextTimestamp) => this.loop(nextTimestamp));
  }

  update(dt) {
    this.state.flash = Math.max(0, this.state.flash - dt * 2.5);
    this.state.spawnAccumulator += dt;

    if (this.state.spawnAccumulator >= this.config.spawnRate) {
      this.state.spawnAccumulator = 0;
      this.spawnObject();
    }

    for (let i = this.state.objects.length - 1; i >= 0; i--) {
      const obj = this.state.objects[i];
      obj.y += obj.speed * dt;

      if (obj.y > this.canvas.height + 30) {
        this.state.objects.splice(i, 1);
        this.state.combo = 0;
        this.state.health = Math.max(0, this.state.health - 10);
      }
    }

    if (this.state.health <= 0) {
      this.state.score = 0;
      this.state.combo = 0;
      this.state.health = 100;
      this.state.objects = [];
    }
  }

  spawnObject() {
    const laneCount = this.config.lanes;
    const laneIndex = Math.floor(Math.random() * laneCount);
    const laneWidth = this.canvas.width / laneCount;
    const x = laneIndex * laneWidth + laneWidth / 2;

    const obj = {
      x,
      y: -12,
      speed: this.config.speed,
      lane: laneIndex,
      key: this.config.keys[laneIndex] ?? 'x',
      hit: false,
      color: this.config.colors[laneIndex] ?? '#63f2b3'
    };

    this.state.objects.push(obj);
  }

  handleInput(key) {
    if (!this.state.objects.length) return;

    const nearby = this.state.objects
      .filter((obj) => obj.key === key)
      .sort((a, b) => Math.abs(a.y - this.canvas.height * 0.78) - Math.abs(b.y - this.canvas.height * 0.78))[0];

    if (!nearby) return;

    const targetY = this.canvas.height * 0.78;
    const diff = Math.abs(nearby.y - targetY);

    if (diff <= 28) {
      this.state.objects = this.state.objects.filter((obj) => obj !== nearby);
      this.state.combo += 1;
      this.state.score += 100 + this.state.combo * 10;
      this.state.health = Math.min(100, this.state.health + 4);
      this.state.flash = 1;

      if (this.audio && this.audio.enabled) {
        this.audio.playTone(this.config.pitch ?? 440, 0.12, 'triangle', 0.02);
      }
    }
  }

  render() {
    const { ctx, canvas } = this;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#0b0d10';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    this.drawBackground();
    this.drawLaneGuides();
    this.drawObjects();
    this.drawHUD();
  }

  drawBackground() {
    const glow = this.state.flash > 0 ? 'rgba(99,242,179,0.18)' : 'rgba(18,26,36,0.9)';
    this.ctx.fillStyle = glow;
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }

  drawLaneGuides() {
    const laneCount = this.config.lanes;
    const laneWidth = this.canvas.width / laneCount;
    const targetY = this.canvas.height * 0.78;

    for (let i = 0; i < laneCount; i++) {
      const x = i * laneWidth;
      this.ctx.strokeStyle = 'rgba(255,255,255,0.12)';
      this.ctx.strokeRect(x, 0, laneWidth, this.canvas.height);
    }

    this.ctx.strokeStyle = '#63f2b3';
    this.ctx.lineWidth = 3;
    this.ctx.beginPath();
    this.ctx.moveTo(0, targetY);
    this.ctx.lineTo(this.canvas.width, targetY);
    this.ctx.stroke();
  }

  drawObjects() {
    for (const obj of this.state.objects) {
      const radius = 16;
      this.ctx.fillStyle = obj.color;
      this.ctx.beginPath();
      this.ctx.arc(obj.x, obj.y, radius, 0, Math.PI * 2);
      this.ctx.fill();

      this.ctx.fillStyle = '#ffffff';
      this.ctx.font = 'bold 12px sans-serif';
      this.ctx.textAlign = 'center';
      this.ctx.textBaseline = 'middle';
      this.ctx.fillText(obj.key.toUpperCase(), obj.x, obj.y + 1);
    }
  }

  drawHUD() {
    const { ctx, canvas } = this;
    ctx.fillStyle = 'rgba(11,13,16,0.8)';
    ctx.fillRect(18, 18, 220, 76);

    ctx.fillStyle = '#e9eef7';
    ctx.font = '18px sans-serif';
    ctx.fillText(`${this.config.label} Mode`, 28, 44);
    ctx.fillText(`Score: ${this.state.score}`, 28, 68);
    ctx.fillText(`Combo: ${this.state.combo}`, 28, 90);

    const healthBarWidth = 220;
    const healthBarHeight = 16;
    ctx.fillStyle = 'rgba(255,255,255,0.15)';
    ctx.fillRect(canvas.width - healthBarWidth - 25, 25, healthBarWidth, healthBarHeight);
    ctx.fillStyle = '#63f2b3';
    ctx.fillRect(canvas.width - healthBarWidth - 25, 25, (this.state.health / 100) * healthBarWidth, healthBarHeight);
  }
}
