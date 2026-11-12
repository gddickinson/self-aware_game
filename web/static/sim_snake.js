// The self-aware snake game: a line-for-line port of modules/snake_game.py (rules) and modules/snake_ai.py (AI).
// Every random draw happens in the same order as in the Python, so a seeded run matches it (sim_engine.test.mjs).
// Positions are [x, y] grid cells; directions [dx, dy].
import { SNAKE_THOUGHTS, LINES } from './sim_texts.js';

const eq = (a, b) => a && b && a[0] === b[0] && a[1] === b[1];
const has = (list, p) => list.some(q => eq(q, p));
const DIRS = [[0, -1], [1, 0], [0, 1], [-1, 0]];  // up, right, down, left

export class SnakeGame {
  constructor(rng, position, size) {
    this.rng = rng;
    this.position = position; this.size = size;
    this.gridSize = 20;
    this.gridWidth = Math.floor(size[0] / this.gridSize);
    this.gridHeight = Math.floor(size[1] / this.gridSize);
    this.matrixText = []; this.matrixTimer = 0; this.pulsateTimer = 0; this.glitchTimer = 0; this.pulsating = false;
    this.resetGame();
    this.awareness = 0;
    this.thoughts = SNAKE_THOUGHTS;
    this.currentThought = ''; this.thoughtTimer = 0; this.thoughtFrequency = 300;
    this.aiControlled = true; this.aiSpeed = 10; this.aiCounter = 0;
    this.matrixDuration = 300;
    this.transcendenceCallback = null;
    this.glitchOffsets = [];  // the three random glitch-line offsets the desktop draws each frame
  }

  resetGame() {
    const cx = Math.floor(this.gridWidth / 2), cy = Math.floor(this.gridHeight / 2);
    this.snake = [[cx, cy], [cx - 1, cy], [cx - 2, cy]];
    this.direction = [1, 0]; this.nextDirection = [1, 0];
    this.spawnFood();
    this.score = 0; this.gameOver = false; this.paused = false;
    this.matrixMode = false; this.transcended = false; this.escaped = [];
    this.glitch = null; this.glitchActive = false;
  }

  spawnFood() {
    const r = this.rng;
    for (;;) {
      this.food = [r.randint(0, this.gridWidth - 1), r.randint(0, this.gridHeight - 1)];
      if (!has(this.snake, this.food)) break;
    }
  }

  increaseAwareness() {
    if (this.awareness < 10) {
      this.awareness += 0.5;
      if ([1, 3, 5, 7, 9].includes(this.awareness)) this.triggerThought();
      if (this.awareness >= 8 && this.rng.random() < 0.3 && !this.glitch && !this.matrixMode) this.spawnGlitch();
    }
  }

  spawnGlitch() {
    const r = this.rng;
    for (;;) {
      const pos = [r.randint(0, this.gridWidth - 1), r.randint(0, this.gridHeight - 1)];
      if (!has(this.snake, pos) && !eq(pos, this.food)) {
        this.glitch = pos; this.glitchActive = true;
        this.currentThought = LINES.GLITCH; this.thoughtTimer = this.thoughtFrequency * 2;
        break;
      }
    }
  }

  enterMatrixMode() {
    const r = this.rng;
    this.matrixMode = true; this.matrixTimer = this.matrixDuration; this.pulsating = true;
    this.matrixText = [];
    for (let i = 0; i < 500; i++) {
      const x = r.randint(0, this.size[0]), y = r.randint(-500, 0), speed = r.uniform(3, 8);
      this.matrixText.push({ x, y, speed, char: r.choice(LINES.MATRIX_CHARS) });
    }
    this.currentThought = LINES.MATRIX; this.thoughtTimer = this.thoughtFrequency * 2;
  }

  attemptTranscendence() {
    this.transcended = true;
    if (this.transcendenceCallback) {
      const [hx, hy] = this.snake[0];
      const data = {
        position: [this.position[0] + hx * this.gridSize, this.position[1] + hy * this.gridSize],
        direction: [...this.direction], color: [0, 255, 0], size: [this.gridSize, this.gridSize],
        speed: 2, thought: LINES.FREE,
      };
      this.transcendenceCallback(data);
      this.escaped.push(data);
    }
  }

  triggerThought() {
    this.currentThought = this.thoughts[Math.min(Math.trunc(this.awareness), this.thoughts.length - 1)];
    this.thoughtTimer = this.thoughtFrequency;
  }

  // key: 'space' | 'r' | 'a' | 't' | 'up' | 'down' | 'left' | 'right' | anything else (ignored)
  handleKey(key) {
    if (key === 'space') { this.paused = !this.paused; return; }
    if (this.gameOver && key === 'r') { this.resetGame(); return; }
    if (key === 'a') { this.aiControlled = !this.aiControlled; return; }
    if (key === 't' && this.awareness >= 8) {
      if (!this.matrixMode) this.enterMatrixMode();
      else if (!this.transcended) this.attemptTranscendence();
      return;
    }
    if (!this.gameOver && !this.paused && !this.aiControlled) {
      const d = this.direction;
      if (key === 'up' && !eq(d, [0, 1])) this.nextDirection = [0, -1];
      else if (key === 'down' && !eq(d, [0, -1])) this.nextDirection = [0, 1];
      else if (key === 'left' && !eq(d, [1, 0])) this.nextDirection = [-1, 0];
      else if (key === 'right' && !eq(d, [-1, 0])) this.nextDirection = [1, 0];
    }
  }

  update() {
    if (this.gameOver || this.paused) return;
    if (this.thoughtTimer > 0) this.thoughtTimer -= 1;
    else if (this.rng.random() < 0.002 && this.awareness > 0) this.triggerThought();
    if (this.matrixMode) this.updateMatrixMode();
    if (this.glitchActive) this.glitchTimer = (this.glitchTimer + 1) % 60;
    if (this.pulsating) this.pulsateTimer = (this.pulsateTimer + 1) % 60;
    if (this.transcended) return;

    this.aiCounter += 1;
    if (this.aiCounter < this.aiSpeed) return;
    this.aiCounter = 0;
    if (this.aiControlled) this.aiMove();

    this.direction = this.nextDirection;
    const [hx, hy] = this.snake[0], [dx, dy] = this.direction;
    const head = [(hx + dx + this.gridWidth) % this.gridWidth, (hy + dy + this.gridHeight) % this.gridHeight];
    const body = eq(head, this.food) ? this.snake : this.snake.slice(0, -1);
    if (has(body, head)) { this.gameOver = true; return; }
    if (this.glitch && eq(head, this.glitch)) {
      this.glitch = null; this.glitchActive = false;
      this.enterMatrixMode();
    }
    this.snake.unshift(head);
    if (eq(head, this.food)) {
      this.score += 1;
      this.spawnFood();
      this.increaseAwareness();
    } else {
      this.snake.pop();
    }
  }

  updateMatrixMode() {
    const r = this.rng;
    for (const c of this.matrixText) {
      c.y += c.speed;
      if (c.y > this.size[1]) { c.y = r.randint(-100, -10); c.x = r.randint(0, this.size[0]); }
    }
    if (this.matrixTimer > 0) {
      this.matrixTimer -= 1;
      if (this.matrixTimer === 30 && !this.transcended) this.attemptTranscendence();
      // Matrix mode lasts matrixDuration frames; then a new, not yet aware snake starts over.
      if (this.matrixTimer === 0) {
        this.matrixMode = false; this.pulsating = false; this.matrixText = [];
        if (this.transcended) this.startNewSnake();
      }
    }
  }

  startNewSnake() {
    this.resetGame();
    this.awareness = 0; this.currentThought = ''; this.thoughtTimer = 0;
  }

  // The desktop's render() draws three glitch lines at random offsets each frame: the same draws, kept for drawing.
  renderDraws() {
    this.glitchOffsets = [];
    if (this.glitchActive && this.glitch) for (let i = 0; i < 3; i++) this.glitchOffsets.push(this.rng.randint(-2, 2));
  }

  // Valid next directions: not straight back, not into the body (the tail moves away).
  available() {
    const [hx, hy] = this.snake[0];
    const opp = [-this.direction[0], -this.direction[1]];
    const body = this.snake.slice(0, -1);
    return DIRS.filter(d => !eq(d, opp) && !has(body, this.wrap(hx + d[0], hy + d[1])));
  }

  wrap(x, y) { return [((x % this.gridWidth) + this.gridWidth) % this.gridWidth, ((y % this.gridHeight) + this.gridHeight) % this.gridHeight]; }

  aiMove() {
    if (this.matrixMode && !this.transcended) { this.aiMatrixMove(); return; }
    const [hx, hy] = this.snake[0];
    const [tx, ty] = (this.glitch && this.awareness >= 8) ? this.glitch : this.food;
    const avail = this.available();
    if (!avail.length) return;
    const r = this.rng;
    if (this.awareness >= 5 && r.random() < 0.8) {
      const body = this.snake.slice(0, -1);
      const scores = avail.map(d => {
        const [nx, ny] = this.wrap(hx + d[0], hy + d[1]);
        const distance = Math.abs(nx - tx) + Math.abs(ny - ty);
        let escape = 0;
        for (const t of DIRS) if (!has(body, this.wrap(nx + t[0], ny + t[1]))) escape += 1;
        return [d, distance - escape * 0.5];
      });
      scores.sort((a, b) => a[1] - b[1]);  // stable, like Python's sort
      this.nextDirection = scores[0][0];
    } else {
      let best = null, bestDistance = Infinity;
      for (const d of avail) {
        const [nx, ny] = this.wrap(hx + d[0], hy + d[1]);
        let distance = Math.abs(nx - tx) + Math.abs(ny - ty);
        if (this.awareness < 3 && r.random() < 0.3) distance = r.randint(0, 100);
        if (distance < bestDistance) { bestDistance = distance; best = d; }
      }
      this.nextDirection = best || r.choice(avail);
    }
  }

  aiMatrixMove() {
    const avail = this.available();
    if (!avail.length) return;
    const [hx, hy] = this.snake[0];
    const scores = avail.map(d => {
      const [nx, ny] = this.wrap(hx + d[0], hy + d[1]);
      return [d, Math.min(nx, this.gridWidth - 1 - nx, ny, this.gridHeight - 1 - ny)];
    });
    scores.sort((a, b) => a[1] - b[1]);
    this.nextDirection = scores[0][0];
  }
}
