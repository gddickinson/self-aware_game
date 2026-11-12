// The whole game: world and buildings (modules/world.py), the dialogue log (modules/dialogue.py) and the main loop
// (main.SelfAwareGame: key handling, update order, transcendence and the world-wide Matrix effect).
// new Game(seed) followed by step(keys) per frame reproduces `python main.py --seed N` frame for frame.
import { PyRandom } from './py_random.js';
import { SnakeGame } from './sim_snake.js';
import { SelfAwareCharacter, TranscendedEntity } from './sim_character.js';
import { LINES } from './sim_texts.js';

// pygame.Rect truncates float coordinates; colliderect needs a strict overlap.
const rect = (p, s) => [Math.trunc(p[0]), Math.trunc(p[1]), s[0], s[1]];
const collide = (a, b) => a[0] < b[0] + b[2] && a[1] < b[1] + b[3] && a[0] + a[2] > b[0] && a[1] + a[3] > b[1];

export class GameWorld {
  constructor(width, height) { this.width = width; this.height = height; this.buildings = new Map(); }
  addBuilding(name, position, size, game = null) {
    const b = { name, position, size, game };
    this.buildings.set(name, b);
    return b;
  }
  getBuilding(name) { return this.buildings.get(name) || null; }
  getBuildings() { return [...this.buildings.values()]; }
  checkCollision(e) {
    const er = rect(e.position, e.size);
    for (const b of this.buildings.values()) if (collide(er, rect(b.position, b.size))) return true;
    const [x, y] = e.position;
    return x < 0 || x + e.size[0] > this.width || y < 0 || y + e.size[1] > this.height;
  }
  update() { for (const b of this.buildings.values()) if (b.game) b.game.update(); }
}

// Last five messages, like the desktop's DialogueSystem (deque(maxlen=5)); frame stamps replace wall-clock time.
export class Dialogue {
  constructor(max = 5) { this.max = max; this.messages = []; }
  add(sender, message, color, frame) {
    this.messages.push({ sender, message, color: color || [255, 255, 255], frame });
    while (this.messages.length > this.max) this.messages.shift();
  }
}

export const WIDTH = 1200, HEIGHT = 800;
// Keys the desktop game understands (main.py + modules/snake_game.py), by the names used in this engine.
export const KEYS = ['p', 'd', 'e', 'm', 'a', 't', 'r', 'space', 'plus', 'minus', 'up', 'down', 'left', 'right'];

export class Game {
  constructor(seed = 1) {
    this.seed = seed;
    const rng = this.rng = new PyRandom(seed);
    this.frame = 0;
    this.width = WIDTH; this.height = HEIGHT;
    this.paused = false; this.debug = false;
    this.world = new GameWorld(WIDTH, HEIGHT);
    this.snake = new SnakeGame(rng, [100, 100], [500, 500]);
    this.world.addBuilding('Snake Game', [100, 100], [500, 500], this.snake);
    this.character = new SelfAwareCharacter(rng, 'Alex', [700, 400], this.world);
    this.dialogue = new Dialogue();
    this.entities = [];
    this.snake.transcendenceCallback = data => this.handleTranscendence(data);
    this.matrixMode = false; this.matrixText = []; this.matrixTimer = 0;
    this.events = [];  // web-only log of what happened, for the inspector ("memories" of this run)
  }

  log(who, text) { this.events.push({ frame: this.frame, who, text }); if (this.events.length > 400) this.events.shift(); }

  handleTranscendence(data) {
    this.entities.push(new TranscendedEntity(this.rng, data));
    this.dialogue.add('SYSTEM', LINES.TRANSCEND_MSG, [0, 255, 0], this.frame);
    this.log('SYSTEM', LINES.TRANSCEND_MSG);
    this.enterMatrixMode();
  }

  enterMatrixMode() {
    const r = this.rng;
    this.matrixMode = true; this.matrixTimer = 300;
    this.matrixText = [];
    for (let i = 0; i < 1000; i++) {
      const x = r.randint(0, this.width), y = r.randint(-this.height, 0), speed = r.uniform(3, 8);
      const char = r.choice(LINES.MATRIX_CHARS);
      this.matrixText.push({ x, y, speed, char, size: r.randint(10, 20) });
    }
  }

  handleKey(key) {
    const s = this.snake;
    if (key === 'p') this.paused = !this.paused;
    else if (key === 'd') this.debug = !this.debug;
    else if (key === 'e') this.character.interact();
    else if (key === 'plus') { if (s.aiSpeed > 1) s.aiSpeed -= 1; }
    else if (key === 'minus') { if (s.aiSpeed < 20) s.aiSpeed += 1; }
    else if (key === 'm' && !this.matrixMode) this.enterMatrixMode();
    s.handleKey(key);
  }

  update() {
    if (this.paused) return;
    if (this.matrixMode) this.updateMatrixMode();
    this.world.update();
    const c = this.character;
    c.update();
    for (const e of this.entities) e.update(this.world);
    if (c.isNearBuilding('Snake Game') && !c.noticedSnakeGame) {
      c.noticedSnakeGame = true;
      this.dialogue.add(c.name, LINES.NOTICE_SNAKE, null, this.frame);
    }
    for (const e of this.entities) {
      if (collide(rect(c.position, c.size), rect(e.position, e.size)) && e.thoughtTimer <= 0) {
        e.thought = LINES.MEET_ENTITY; e.thoughtTimer = 180;
        c.triggerThought(LINES.MEET_ENTITY_CHAR);
      }
    }
  }

  updateMatrixMode() {
    const r = this.rng;
    for (const c of this.matrixText) {
      c.y += c.speed;
      if (c.y > this.height) { c.y = r.randint(-100, -10); c.x = r.randint(0, this.width); }
    }
    if (this.matrixTimer > 0) {
      this.matrixTimer -= 1;
      if (this.matrixTimer === 0) this.matrixMode = false;
    }
  }

  // One frame of the desktop loop: keys, update, then render's random draws (snake glitch lines).
  step(keys = []) {
    this.frame += 1;
    const before = this.watch();
    for (const k of keys) this.handleKey(k);
    this.update();
    this.snake.renderDraws();
    this.noteChanges(before);
  }

  // What the inspector's event log tracks between frames.
  watch() {
    const c = this.character, s = this.snake;
    return { ct: c.currentThought, cs: c.state, st: s.currentThought, sa: s.awareness, so: s.gameOver,
      sm: s.matrixMode, dl: this.dialogue.messages.length && this.dialogue.messages.at(-1), et: this.entities.map(e => e.thought + e.thoughtTimer) };
  }

  noteChanges(b) {
    const c = this.character, s = this.snake;
    if (c.state !== b.cs) this.log(c.name, `state ${b.cs} -> ${c.state}`);
    if (c.currentThought && c.currentThought !== b.ct) this.log(c.name, `thinks: "${c.currentThought}"`);
    if (s.awareness !== b.sa) this.log('Snake', `awareness ${b.sa} -> ${s.awareness}`);
    if (s.currentThought && s.currentThought !== b.st) this.log('Snake', `thinks: "${s.currentThought}"`);
    if (s.gameOver && !b.so) this.log('Snake', 'game over (press R to restart)');
    if (s.matrixMode && !b.sm) this.log('Snake', 'entered Matrix mode');
    const last = this.dialogue.messages.at(-1);
    if (last && last !== b.dl && last.sender !== 'SYSTEM') this.log(last.sender, `says: "${last.message}"`);
    this.entities.forEach((e, i) => { if (b.et[i] !== undefined && e.thoughtTimer === 180 && e.thought === LINES.MEET_ENTITY && b.et[i] !== e.thought + 180) this.log('Entity', `says: "${e.thought}"`); });
  }
}
