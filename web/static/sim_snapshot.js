// Engine state in the same shape as web/sim_record.py's snapshot() of the Python game, and a tolerant comparison.
// Used by sim_engine.test.mjs (node) and the Verify page (browser) to check the JS run against the Python one.
const xy = p => (p ? [p[0], p[1]] : null);

export function snapshot(g) {
  const c = g.character, s = g.snake;
  return {
    frame: g.frame, paused: g.paused, matrix: g.matrixMode, matrixTimer: g.matrixTimer,
    rain: g.matrixText.slice(0, 3).map(m => [m.x, m.y]),
    char: { pos: xy(c.position), state: c.state, stateTimer: c.stateTimer, stateDuration: c.stateDuration, dir: c.direction, target: xy(c.target),
      thought: c.currentThought, thoughtTimer: c.thoughtTimer, noticed: c.noticedSnakeGame, anim: c.animFrame },
    snake: { body: s.snake.map(xy), dir: xy(s.direction), next: xy(s.nextDirection), food: xy(s.food), score: s.score,
      awareness: s.awareness, over: s.gameOver, paused: s.paused, ai: s.aiControlled, speed: s.aiSpeed,
      counter: s.aiCounter, thought: s.currentThought, thoughtTimer: s.thoughtTimer, glitch: xy(s.glitch),
      matrix: s.matrixMode, matrixTimer: s.matrixTimer, transcended: s.transcended,
      rain: s.matrixText.slice(0, 3).map(m => [m.x, m.y]) },
    entities: g.entities.map(e => ({ pos: xy(e.position), dir: xy(e.direction), thought: e.thought,
      thoughtTimer: e.thoughtTimer, target: xy(e.target), timer: e.timer, stream: [e.stream[0].x, e.stream[0].y] })),
    dialogue: g.dialogue.messages.map(m => [m.sender, m.message]),
  };
}

// First difference between a Python snapshot and a JS one ('' if they agree; numbers within 1e-7).
export function diff(py, js, path = '') {
  if (typeof py === 'number' && typeof js === 'number') {
    return Math.abs(py - js) <= 1e-7 * Math.max(1, Math.abs(py)) ? '' : `${path}: python ${py} js ${js}`;
  }
  if (Array.isArray(py) || (py && typeof py === 'object')) {
    if (!js || typeof js !== 'object') return `${path}: python ${JSON.stringify(py)} js ${JSON.stringify(js)}`;
    const keys = Array.isArray(py) ? [...Array(Math.max(py.length, js.length)).keys()] : Object.keys(py);
    if (Array.isArray(py) && py.length !== js.length) return `${path}: length python ${py.length} js ${js.length}`;
    for (const k of keys) { const d = diff(py[k], js[k], `${path}.${k}`); if (d) return d; }
    return '';
  }
  return py === js ? '' : `${path}: python ${JSON.stringify(py)} js ${JSON.stringify(js)}`;
}

// Replay a recorded Python run in a fresh engine; returns { checked, first } (first = first mismatch or null).
export function replay(GameClass, rec) {
  const g = new GameClass(rec.seed);
  const snaps = new Map(rec.snaps.map(s => [s.frame, s]));
  let checked = 0, first = null;
  const check = () => {
    const py = snaps.get(g.frame);
    if (!py) return;
    checked += 1;
    const d = diff(py, snapshot(g));
    if (d && !first) first = `frame ${g.frame} ${d}`;
  };
  check();
  for (let f = 1; f <= rec.frames && !first; f++) { g.step(rec.keys[f] || []); check(); }
  if (!first) {
    const d = diff(rec.rng, [0, 1, 2, 3].map(() => g.rng.random()), '.rng');
    if (d) first = `after frame ${rec.frames} ${d}`;
  }
  return { checked, first };
}
