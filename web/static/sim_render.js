// Canvas drawing of the game, following the desktop's render() methods (main.py, modules/world.py,
// modules/snake_render.py, modules/character.py, modules/entities.py, modules/dialogue.py, modules/debug.py):
// same colours, positions and sizes on a 1200x800 canvas. Drawing never touches the simulation or its RNG.
import { CONTROLS_HELP } from './sim_texts.js';

const rgb = (c, a = 1) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;
const FONT = px => `bold ${Math.round(px * 0.66)}px Arial, Helvetica, sans-serif`;  // ~ pygame Font(None, px) (freesansbold)
let sprites = null;
if (typeof Image !== 'undefined') { sprites = new Image(); sprites.src = 'static/character_sprites.png'; }

function wrap(ctx, text, maxW) {
  const lines = []; let line = '';
  for (const w of text.split(' ')) {
    const test = line + w + ' ';
    if (ctx.measureText(test).width < maxW) line = test; else { lines.push(line); line = w + ' '; }
  }
  if (line) lines.push(line);
  return lines;
}

function roundRect(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.fill(); }

// A thought bubble (text wrapped at maxW) beside an anchor box, flipped to stay on screen, with three trailing dots.
function bubble(ctx, text, { ax, ay, aw, ah, fontPx, lineH, maxW, fill, dot, limitW, dotR = [6, 4, 2], dotStep = 6 }) {
  ctx.font = FONT(fontPx);
  const lines = wrap(ctx, text, maxW);
  const w = Math.max(...lines.map(l => ctx.measureText(l).width)) + 20, h = lines.length * lineH + 10;
  let x = ax + aw + 5, y = ay - (lineH === 25 ? 60 : 40);
  if (x + w > limitW) x = ax - 5 - w;
  if (y < 0) y = ay + ah + 5;
  ctx.fillStyle = fill; roundRect(ctx, x, y, w, h, 10);
  ctx.fillStyle = '#000'; ctx.textBaseline = 'top';
  lines.forEach((l, i) => ctx.fillText(l, x + 10, y + 5 + i * lineH + 2));
  ctx.fillStyle = dot;
  for (let i = 0; i < 3; i++) {
    const cx = x > ax + aw / 2 ? x - 10 + i * dotStep : x + w + 4 - i * dotStep;
    ctx.beginPath(); ctx.arc(cx, y + h + i * (dotStep - 1), dotR[i], 0, Math.PI * 2); ctx.fill();
  }
}

function drawSnakeGame(ctx, s) {
  const [ox, oy] = s.position, [W, H] = s.size, gs = s.gridSize;
  ctx.save(); ctx.translate(ox, oy);
  ctx.beginPath(); ctx.rect(0, 0, W, H); ctx.clip();
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  ctx.textBaseline = 'top';
  if (s.matrixMode) {
    ctx.font = FONT(20);
    for (const c of s.matrixText) {
      if (c.y < 0 || c.y > H || c.x < 0 || c.x > W) continue;
      ctx.fillStyle = rgb([0, Math.max(0, Math.min(255, 255 - c.y * 0.5)), 0]); ctx.fillText(c.char, c.x, c.y);
    }
  }
  ctx.strokeStyle = 'rgb(20,20,20)'; ctx.lineWidth = 1; ctx.beginPath();
  for (let x = 0; x < W; x += gs) { ctx.moveTo(x + 0.5, 0); ctx.lineTo(x + 0.5, H); }
  for (let y = 0; y < H; y += gs) { ctx.moveTo(0, y + 0.5); ctx.lineTo(W, y + 0.5); }
  ctx.stroke();
  ctx.fillStyle = 'rgb(255,0,0)'; ctx.fillRect(s.food[0] * gs, s.food[1] * gs, gs, gs);
  if (s.glitchActive && s.glitch) {
    const pulse = Math.abs(Math.sin(s.glitchTimer * 0.1)) * 0.5 + 0.5;
    const gx = s.glitch[0] * gs, gy = s.glitch[1] * gs;
    ctx.fillStyle = rgb([0, 255, Math.trunc(255 * pulse)]); ctx.fillRect(gx, gy, gs, gs);
    ctx.strokeStyle = '#fff'; ctx.beginPath();
    for (const off of s.glitchOffsets) { ctx.moveTo(gx + off, gy); ctx.lineTo(gx + gs + off, gy + gs); }
    ctx.stroke();
  }
  if (!s.transcended) {
    s.snake.forEach(([x, y], i) => {
      let col = i === 0 ? [0, 255, 0] : [0, 200, 0];
      if (s.matrixMode) { const p = s.pulsating ? Math.abs(Math.sin(s.pulsateTimer * 0.1)) * 0.5 + 0.5 : 1; col = [0, 255, 0].map((v, k) => (k === 1 ? v : Math.trunc(v * p))); }
      ctx.fillStyle = rgb(col); ctx.fillRect(x * gs, y * gs, gs, gs);
    });
  }
  ctx.font = FONT(36); ctx.fillStyle = '#fff';
  ctx.fillText(`Score: ${s.score}`, 10, 10);
  if (s.awareness > 0) ctx.fillText(`Awareness: ${Math.trunc(s.awareness)}`, 10, 50);
  if (s.aiControlled) { ctx.fillStyle = 'rgb(100,200,255)'; ctx.fillText('AI Mode', W - 100, 10); }
  if (s.thoughtTimer > 0 && s.currentThought) {
    const [hx, hy] = s.snake[0];
    bubble(ctx, s.currentThought, { ax: hx * gs, ay: hy * gs, aw: gs, ah: gs, fontPx: 24, lineH: 25, maxW: 200,
      fill: s.matrixMode ? 'rgba(0,255,0,.7)' : 'rgba(200,200,255,.7)', dot: s.matrixMode ? 'rgb(0,255,0)' : 'rgb(200,200,255)', limitW: W });
  }
  ctx.font = FONT(36); ctx.textAlign = 'center';
  if (s.matrixMode) {
    ctx.fillStyle = 'rgb(0,255,0)'; ctx.fillText('MATRIX MODE', W / 2, 10);
    if (s.transcended) ctx.fillText('TRANSCENDING...', W / 2, H / 2);
  }
  if (s.gameOver) {
    ctx.font = FONT(72); ctx.fillStyle = 'rgb(255,0,0)'; ctx.fillText('Game Over', W / 2, H / 2 - 25);
    ctx.font = FONT(36); ctx.fillStyle = '#fff'; ctx.fillText('Press R to restart', W / 2, H / 2 + 25);
  }
  if (s.paused) { ctx.font = FONT(72); ctx.fillStyle = '#fff'; ctx.fillText('PAUSED', W / 2, H / 2 - 25); }
  ctx.textAlign = 'left';
  ctx.restore();
}

function drawBuildings(ctx, g, selected) {
  for (const b of g.world.getBuildings()) {
    const [x, y] = b.position, [w, h] = b.size;
    if (b.game) drawSnakeGame(ctx, b.game);
    const border = selected === 'snake' ? 'rgb(255,255,0)' : 'rgb(50,50,50)';
    ctx.strokeStyle = border; ctx.lineWidth = 3; ctx.strokeRect(x + 1.5, y + 1.5, w - 3, h - 3);
    ctx.font = FONT(20); const tw = ctx.measureText(b.name).width + 10;
    ctx.fillStyle = '#000'; ctx.fillRect(x, y - 20, tw, 20);
    ctx.lineWidth = 1; ctx.strokeRect(x + 0.5, y - 19.5, tw - 1, 19);
    ctx.fillStyle = '#fff'; ctx.textBaseline = 'top'; ctx.fillText(b.name, x + 5, y - 17);
  }
}

function drawCharacter(ctx, c, selected) {
  const [x, y] = c.position, [w, h] = c.size;
  if (sprites && sprites.complete && sprites.naturalWidth) {
    const fw = sprites.naturalWidth / 4, fh = sprites.naturalHeight / 4;
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(sprites, c.animFrame * fw, c.direction * fh, fw, fh, x, y, w, h);
  } else {
    ctx.fillStyle = 'rgb(100,150,250)'; ctx.fillRect(x, y, w, h);
  }
  if (selected) { ctx.strokeStyle = '#ff0'; ctx.lineWidth = 2; ctx.strokeRect(x - 3, y - 3, w + 6, h + 6); }
  if (c.thoughtTimer > 0 && c.currentThought) {
    bubble(ctx, c.currentThought, { ax: x, ay: y, aw: w, ah: h, fontPx: 20, lineH: 25, maxW: 200,
      fill: 'rgba(255,255,255,.7)', dot: '#fff', limitW: c.world.width });
  }
}

function drawEntity(ctx, e, selected) {
  const [x, y] = e.position, [w, h] = e.size;
  ctx.fillStyle = rgb(e.color); ctx.fillRect(x, y, w, h);
  const cx = x + Math.floor(w / 2), cy = y + Math.floor(h / 2);
  ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.beginPath();
  ctx.moveTo(cx, cy); ctx.lineTo(cx + e.direction[0] * 15, cy + e.direction[1] * 15); ctx.stroke();
  ctx.font = FONT(12); ctx.fillStyle = 'rgb(0,255,0)'; ctx.textBaseline = 'top';
  for (const c of e.stream) ctx.fillText(c.char, cx + c.x, cy + c.y);
  if (selected) { ctx.strokeStyle = '#ff0'; ctx.strokeRect(x - 3, y - 3, w + 6, h + 6); }
  if (e.thoughtTimer > 0) {
    bubble(ctx, e.thought, { ax: x, ay: y, aw: w, ah: h, fontPx: 18, lineH: 20, maxW: 150,
      fill: 'rgba(0,255,0,.7)', dot: 'rgb(0,255,0)', limitW: 1200, dotR: [4, 3, 2], dotStep: 5 });
  }
}

function drawMatrix(ctx, g) {
  ctx.fillStyle = 'rgba(0,0,0,.39)'; ctx.fillRect(0, 0, g.width, g.height);
  ctx.textBaseline = 'top';
  for (const c of g.matrixText) {
    if (c.y < 0 || c.y > g.height || c.x < 0 || c.x > g.width) continue;
    ctx.font = FONT(c.size); ctx.fillStyle = rgb([0, Math.max(0, Math.min(255, 255 - c.y * 0.5)), 0]);
    ctx.fillText(c.char, c.x, c.y);
  }
}

// Dialogue box (bottom centre, 800x150); messages fade after 5 s over 2 s of game time (60 frames a second).
function drawDialogue(ctx, g) {
  const msgs = g.dialogue.messages;
  if (!msgs.length) return;
  const W = 800, H = 150, x = g.width / 2 - W / 2, y = g.height - 100 - H;
  ctx.fillStyle = 'rgba(0,0,0,.7)'; roundRect(ctx, x, y, W, H, 10);
  ctx.font = FONT(24); ctx.textBaseline = 'top';
  let yo = 10;
  for (const m of msgs) {
    const age = (g.frame - m.frame) / 60;
    let a = 1;
    if (age > 5) { const p = (age - 5) / 2; if (p >= 1) continue; a = 1 - p; }
    ctx.fillStyle = rgb(m.color, a); const label = `${m.sender}:`; ctx.fillText(label, x + 10, y + yo);
    ctx.fillStyle = rgb([255, 255, 255], a); ctx.fillText(m.message, x + 15 + ctx.measureText(label).width, y + yo);
    yo += 30;
  }
}

function drawDebug(ctx, g, fps) {
  const c = g.character, s = g.snake;
  const rows = [[`FPS: ${fps.toFixed(1)}`, 'rgb(255,255,0)'], ['Character', 'rgb(200,200,0)', 1],
    [`  Position: (${c.position[0].toFixed(1)}, ${c.position[1].toFixed(1)})`, '#fff'],
    [`  State: ${c.state}, Awareness: ${c.selfAwareness.toFixed(1)}`, '#fff'], ['Snake Game', 'rgb(200,200,0)', 1],
    [`  Score: ${s.score}, Awareness: ${s.awareness.toFixed(1)}`, '#fff'],
    [`  AI: ${s.aiControlled ? 'On' : 'Off'}, Speed: ${s.aiSpeed}`, '#fff']];
  ctx.font = FONT(18); ctx.textBaseline = 'top';
  rows.forEach(([t, col, under], i) => {
    ctx.fillStyle = col; ctx.fillText(t, 10, 10 + i * 20);
    if (under) ctx.fillRect(10, 10 + i * 20 + 15, ctx.measureText(t).width, 1);
  });
}

export function draw(ctx, g, { selected = 'alex', fps = 0 } = {}) {
  ctx.fillStyle = 'rgb(100,150,100)'; ctx.fillRect(0, 0, g.width, g.height);
  ctx.strokeStyle = 'rgb(120,170,120)'; ctx.lineWidth = 1; ctx.beginPath();
  for (let x = 0; x < g.width; x += 50) { ctx.moveTo(x + 0.5, 0); ctx.lineTo(x + 0.5, g.height); }
  for (let y = 0; y < g.height; y += 50) { ctx.moveTo(0, y + 0.5); ctx.lineTo(g.width, y + 0.5); }
  ctx.stroke();
  drawBuildings(ctx, g, selected);
  g.entities.forEach((e, i) => drawEntity(ctx, e, selected === `entity${i}`));
  drawCharacter(ctx, g.character, selected === 'alex');
  if (g.matrixMode) drawMatrix(ctx, g);
  drawDialogue(ctx, g);
  if (g.debug) drawDebug(ctx, g, fps);
  if (g.paused) {
    ctx.font = FONT(74); ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('PAUSED', g.width / 2, g.height / 2); ctx.textAlign = 'left';
  }
  ctx.font = FONT(20); ctx.fillStyle = 'rgb(200,200,200)'; ctx.textBaseline = 'top'; ctx.textAlign = 'right';
  CONTROLS_HELP.forEach((t, i) => ctx.fillText(t, g.width - 10, 10 + i * 20));
  ctx.textAlign = 'left';
}

// Which thing is under canvas point (x, y): 'alex', 'entity<i>', 'snake' or null.
export function hit(g, x, y) {
  const inside = (p, s, pad = 6) => x >= p[0] - pad && x <= p[0] + s[0] + pad && y >= p[1] - pad && y <= p[1] + s[1] + pad;
  if (inside(g.character.position, g.character.size)) return 'alex';
  const i = g.entities.findIndex(e => inside(e.position, e.size));
  if (i >= 0) return `entity${i}`;
  if (inside(g.snake.position, g.snake.size, 0)) return 'snake';
  return null;
}
