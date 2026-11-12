// The roaming self-aware character (modules/character.py) and the transcended snake entity (modules/entities.py),
// ported line for line: same states, timers, thought choices and random draws in the same order as the Python.
import { CHARACTER_THOUGHTS, SNAKE_GAME_OBSERVATIONS, FOURTH_WALL_THOUGHTS, LINES } from './sim_texts.js';

export const STATES = ['IDLE', 'WALKING', 'THINKING', 'INVESTIGATING', 'CONFUSED', 'INTERACTING'];

export class SelfAwareCharacter {
  constructor(rng, name, position, world) {
    this.rng = rng; this.name = name; this.world = world;
    this.position = [...position];
    this.speed = 2; this.size = [30, 60];
    this.direction = 0;  // 0 right, 1 down, 2 left, 3 up (sprite-sheet row)
    this.animFrame = 0; this.animSpeed = 0.1; this.animTimer = 0;
    this.state = 'IDLE'; this.stateTimer = 0; this.target = null;
    this.selfAwareness = 8.5;  // 0-10 scale; fixed in the Python (the character starts self-aware)
    this.thoughts = CHARACTER_THOUGHTS;
    this.currentThought = ''; this.thoughtTimer = 0;
    this.noticedSnakeGame = false;
    this.observations = SNAKE_GAME_OBSERVATIONS;
  }

  triggerThought(specific = null) {
    this.currentThought = specific || this.rng.choice(this.thoughts);
    this.thoughtTimer = this.rng.randint(180, 300);
  }

  changeState(s) {
    const r = this.rng, w = this.world;
    this.state = s; this.stateTimer = 0;
    if (s === 'IDLE') this.stateTimer = r.randint(60, 180);
    else if (s === 'WALKING') {
      const x = r.randint(50, w.width - 50);
      this.target = [x, r.randint(50, w.height - 50)];
    } else if (s === 'THINKING') { this.stateTimer = r.randint(120, 240); this.triggerThought(); }
    else if (s === 'INVESTIGATING') {
      const bs = w.getBuildings();
      if (bs.length) {
        const b = r.choice(bs);
        const x = b.position[0] + r.randint(0, b.size[0]);
        this.target = [x, b.position[1] + r.randint(0, b.size[1])];
      }
    } else if (s === 'CONFUSED') { this.stateTimer = r.randint(90, 150); this.triggerThought(LINES.CONFUSED); }
  }

  // One step toward the target; returns 'arrived', 'blocked' or 'moving'.
  stepToTarget() {
    const p = this.position, t = this.target;
    const dx = t[0] - p[0], dy = t[1] - p[1];
    const distance = Math.sqrt(dx * dx + dy * dy);
    if (Math.abs(dx) > Math.abs(dy)) this.direction = dx < 0 ? 2 : 0;
    else this.direction = dy < 0 ? 3 : 1;
    if (distance < this.speed) { this.position = [...t]; return 'arrived'; }
    const mx = (dx / distance) * this.speed, my = (dy / distance) * this.speed;
    p[0] += mx; p[1] += my;
    if (this.world.checkCollision(this)) { p[0] -= mx; p[1] -= my; return 'blocked'; }
    return 'moving';
  }

  update() {
    const r = this.rng;
    this.animTimer += this.animSpeed;
    if (this.animTimer >= 1) { this.animTimer = 0; this.animFrame = (this.animFrame + 1) % 4; }
    if (this.thoughtTimer > 0) {
      this.thoughtTimer -= 1;
      if (this.thoughtTimer === 0) this.currentThought = '';
    }
    this.stateTimer += 1;
    const s = this.state;
    if (s === 'IDLE') {
      if (this.stateTimer > 60 && r.random() < 0.01 && !this.currentThought) this.triggerThought();
      if (this.stateTimer >= r.randint(180, 360)) {
        const choices = [['WALKING', 0.5], ['THINKING', 0.3], ['INVESTIGATING', 0.15], ['CONFUSED', 0.05]];
        let total = 0;
        for (const [, w] of choices) total += w;
        const x = r.uniform(0, total);
        let upto = 0;
        for (const [st, w] of choices) { upto += w; if (upto >= x) { this.changeState(st); break; } }
      }
    } else if (s === 'WALKING') {
      if (this.target) {
        const res = this.stepToTarget();
        if (res === 'arrived') { this.target = null; this.changeState('IDLE'); }
        else if (res === 'blocked') this.changeState('CONFUSED');
      } else this.changeState('IDLE');
    } else if (s === 'THINKING') {
      if (this.stateTimer >= r.randint(180, 300)) this.changeState('IDLE');
    } else if (s === 'INVESTIGATING') {
      if (this.target) {
        const res = this.stepToTarget();
        if (res !== 'moving') this.finishInvestigation();
      } else this.changeState('IDLE');
    } else if (s === 'CONFUSED') {
      if (this.stateTimer >= 120) this.changeState('IDLE');
    } else if (s === 'INTERACTING') {
      if (this.stateTimer >= 180) this.changeState('IDLE');
    }
  }

  finishInvestigation() {
    this.target = null;
    this.changeState('THINKING');
    if (this.isNearBuilding('Snake Game')) this.triggerThought(this.rng.choice(this.observations));
  }

  interact() {
    this.changeState('INTERACTING');
    this.triggerThought(this.rng.choice(FOURTH_WALL_THOUGHTS));
  }

  // Distance from the character's centre to the building's rectangle (0 inside) under 100 px.
  isNearBuilding(name) {
    const b = this.world.getBuilding(name);
    if (!b) return false;
    const cx = this.position[0] + Math.floor(this.size[0] / 2), cy = this.position[1] + Math.floor(this.size[1] / 2);
    const [bx, by] = b.position, [bw, bh] = b.size;
    const dx = Math.max(bx - cx, 0, cx - (bx + bw)), dy = Math.max(by - cy, 0, cy - (by + bh));
    return Math.sqrt(dx * dx + dy * dy) < 100;
  }
}

export class TranscendedEntity {
  constructor(rng, data) {
    this.rng = rng;
    this.position = data.position; this.direction = data.direction; this.color = data.color;
    this.size = data.size; this.speed = data.speed; this.thought = data.thought;
    this.thoughtTimer = 180;
    this.target = null; this.timer = 0;
    this.stream = [];
    for (let i = 0; i < 20; i++) {
      const x = rng.randint(-10, 10), y = rng.randint(-20, 0), char = rng.choice('01');
      this.stream.push({ x, y, char, speed: rng.uniform(1, 3) });
    }
  }

  update(world) {
    const r = this.rng;
    if (this.thoughtTimer > 0) this.thoughtTimer -= 1;
    for (const c of this.stream) {
      c.y += c.speed;
      if (c.y > 20) { c.y = r.randint(-20, -10); c.x = r.randint(-10, 10); }
    }
    if (!this.target || this.timer <= 0) {
      const x = r.randint(50, world.width - 50);
      this.target = [x, r.randint(50, world.height - 50)];
      this.timer = r.randint(180, 360);
    } else {
      this.timer -= 1;
      const dx = this.target[0] - this.position[0], dy = this.target[1] - this.position[1];
      const distance = Math.sqrt(dx * dx + dy * dy);
      if (distance < this.speed) { this.position = [...this.target]; this.target = null; }
      else {
        const mx = (dx / distance) * this.speed, my = (dy / distance) * this.speed;
        this.position[0] += mx; this.position[1] += my;
        if (Math.abs(mx) > Math.abs(my)) this.direction = mx > 0 ? [1, 0] : [-1, 0];
        else this.direction = my > 0 ? [0, 1] : [0, -1];
      }
    }
  }
}
