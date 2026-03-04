export class HitCircle { constructor(x, y, time) { this.x = x; this.y = y; this.time = time; this.hit = false; } }
export class Slider { constructor(points, duration) { this.points = points; this.duration = duration; this.hit = false; } }
export class Spinner { constructor(duration) { this.duration = duration; this.hit = false; } }
export class SliderPoint { constructor(x,y){ this.x=x; this.y=y; } }
export class TaikoNote { constructor(time, type){ this.time = time; this.type = type; this.hit = false; } }
export class Fruit { constructor(x, y, time){ this.x=x; this.y=y; this.time=time; this.hit=false; } }
export class ManiaNote { constructor(lane, time, duration=0){ this.lane=lane; this.time=time; this.duration=duration; this.hit=false; } }
