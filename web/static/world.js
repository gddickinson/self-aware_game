// World page: the game running in the browser (JS port of the Python), canvas view, controls, keys and inspector.
import { route, app, $, $$, esc, api, isStatic, animate, needsServer } from './core.js';
import { Game } from './sim_world.js';
import { draw, hit } from './sim_render.js';
import { tabs, inspect, eventLog } from './inspector.js';
import { replay } from './sim_snapshot.js';

const SPEEDS = [0.25, 0.5, 1, 2, 4, 8, 16];
const KEYMAP = { p: 'p', d: 'd', e: 'e', m: 'm', a: 'a', t: 't', r: 'r', ' ': 'space', '+': 'plus', '=': 'plus',
  '-': 'minus', ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right' };
const BUTTONS = [['e', 'E', 'Interact with Alex'], ['a', 'A', 'Toggle snake AI'], ['space', 'Space', 'Pause the snake game'],
  ['t', 'T', 'Trigger transcendence (snake awareness 8+)'], ['r', 'R', 'Restart the snake after game over'],
  ['plus', '+', 'Snake faster'], ['minus', '-', 'Snake slower'], ['m', 'M', 'Force world Matrix mode'],
  ['p', 'P', 'Pause the world (desktop P)'], ['d', 'D', 'Toggle debug overlay'],
  ['up', '↑', 'Snake up'], ['left', '←', 'Snake left'], ['down', '↓', 'Snake down'], ['right', '→', 'Snake right']];

route('world', (args, query) => {
  let seed = Number.isInteger(+query.seed) && +query.seed >= 0 ? +query.seed : 0;
  let g, keys, pending, running = true, speed = 1, acc = 0, selected = 'alex', last = 0, fps = 0, lastTabs = '';
  const reset = () => { g = new Game(seed); keys = {}; pending = []; acc = 0; };
  reset();

  app().innerHTML = `
  <p class="kicker">The simulation</p>
  <h1 class="glow">World</h1>
  <p class="lead">Alex wanders the world and wonders whether it is in a game; inside the building a snake plays Snake,
  grows aware with every meal, finds a glitch and escapes into Alex's world. Same seed, same run as <code>python main.py --seed ${seed}</code>.</p>
  <div class="play">
    <div>
      <div class="stage" id="stage" tabindex="0" aria-label="Game world: click a character to inspect it; keys work like the desktop game">
        <canvas id="cv" width="1200" height="800">The game world: Alex, the snake game and any transcended entities.</canvas>
      </div>
      <div class="bar" role="toolbar" aria-label="Simulation controls">
        <button type="button" id="play">Pause</button>
        <button type="button" class="alt" id="step" title="Advance one frame">Step</button>
        <button type="button" class="alt" id="sec" title="Advance 60 frames (1 s)">+1 s</button>
        <button type="button" class="alt" id="ff" title="Advance 1000 frames (about 17 s)">+1000</button>
        <span class="seg" id="speeds" role="group" aria-label="Speed">${SPEEDS.map(s => `<button type="button" data-s="${s}">${s}×</button>`).join('')}</span>
      </div>
      <div class="row seedrow">
        <div><label for="seed">Seed</label><input id="seed" type="number" min="0" step="1" value="${seed}"></div>
        <div><button type="button" id="restart">Restart run</button><button type="button" class="alt" id="rand">Random seed</button></div>
      </div>
      <h3>Keys <small class="mute">(as in the desktop game; keyboard works too)</small></h3>
      <div class="keys">${BUTTONS.map(([k, l, t]) => `<button type="button" class="alt key" data-k="${k}" title="${esc(t)}" aria-label="${esc(t)}">${l}</button>`).join('')}</div>
      <p class="hint" id="keylog"></p>
      <div class="check panel">
        <b>Check this run with Python</b>
        ${isStatic() ? needsServer('Replaying your run (seed and key presses) through the Python game')
    : '<p class="small mute">Plays the same seed and key presses through the real desktop code (headless) and compares every 10th frame.</p><button type="button" id="check">Check with Python</button><span id="checkout" class="small"></span>'}
      </div>
    </div>
    <aside class="controls panel" aria-label="Inspector">
      <div class="seg tabs" id="tabs"></div>
      <div id="insp"></div>
      <h3>Event log</h3>
      <ol class="events" id="events"></ol>
      <p class="hint">The event log is kept by this web page (the Python logs these events to debug.log).</p>
    </aside>
  </div>`;

  const cv = $('#cv'), ctx = cv.getContext('2d');
  const render = () => {
    draw(ctx, g, { selected, fps });
    const tabsKey = `${selected}/${g.entities.length}`;  // rebuild the tab buttons only when they change
    if (tabsKey !== lastTabs) { $('#tabs').innerHTML = tabs(g, selected); lastTabs = tabsKey; }
    $('#insp').innerHTML = inspect(g, selected);
    $('#events').innerHTML = eventLog(g);
    $('#play').textContent = running ? 'Pause' : 'Play';
    $$('#speeds button').forEach(b => b.classList.toggle('on', +b.dataset.s === speed));
    const n = Object.values(keys).reduce((a, k) => a + k.length, 0);
    $('#keylog').textContent = `Frame ${g.frame} · ${n} key press${n === 1 ? '' : 'es'} recorded${pending.length ? ` · next frame: ${pending.join(', ')}` : ''}`;
  };
  const stepN = n => {
    for (let i = 0; i < n; i++) {
      const k = pending; pending = [];
      if (k.length) keys[g.frame + 1] = (keys[g.frame + 1] || []).concat(k);
      g.step(k);
    }
  };
  const press = k => {
    pending.push(k);
    if (!running) stepN(1);  // paused: the key is handled at the start of the next frame, so play that frame
    render();
  };

  let inspTick = 0;
  animate(t => {
    const dt = last ? Math.min(0.1, (t - last) / 1000) : 0;
    if (dt > 0) fps = fps * 0.9 + (1 / dt) * 0.1;
    last = t;
    if (running) {
      acc += dt * 60 * speed;
      const n = Math.min(400, Math.floor(acc));
      acc -= n;
      stepN(n);
    }
    draw(ctx, g, { selected, fps });
    if (++inspTick % 6 === 0 || !running) render();
  });

  $('#play').onclick = () => { running = !running; render(); };
  $('#step').onclick = () => { running = false; stepN(1); render(); };
  $('#sec').onclick = () => { stepN(60); render(); };
  $('#ff').onclick = () => { stepN(1000); render(); };
  $('#speeds').onclick = e => { const b = e.target.closest('button'); if (b) { speed = +b.dataset.s; render(); } };
  const restart = () => { seed = Math.max(0, Math.trunc(+$('#seed').value || 0)); $('#seed').value = seed; reset(); history.replaceState(null, '', `#/world?seed=${seed}`); render(); };
  $('#restart').onclick = restart;
  $('#seed').onkeydown = e => { if (e.key === 'Enter') restart(); };
  $('#rand').onclick = () => { $('#seed').value = Math.floor(Math.random() * 100000); restart(); };
  $$('.keys .key').forEach(b => { b.onclick = () => press(b.dataset.k); });
  $('#tabs').onclick = e => { const b = e.target.closest('button'); if (b) { selected = b.dataset.sel; render(); } };
  cv.addEventListener('click', e => {
    const r = cv.getBoundingClientRect();
    const who = hit(g, (e.clientX - r.left) * (cv.width / r.width), (e.clientY - r.top) * (cv.height / r.height));
    if (who === 'alex' && selected === 'alex') press('e');  // clicking Alex again interacts, like the E key
    if (who) { selected = who; render(); }
  });
  const onKey = e => {
    const tag = e.target.tagName;
    if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA' || e.metaKey || e.ctrlKey || e.altKey) return;
    if (tag === 'BUTTON' && (e.key === ' ' || e.key === 'Enter')) return;
    const k = KEYMAP[e.key.length === 1 ? e.key.toLowerCase() : e.key];
    if (!k) return;
    e.preventDefault();
    press(k);
  };
  document.addEventListener('keydown', onKey);
  // animate() stops the loop when the route changes; the key listener goes with it.
  window.addEventListener('hashchange', () => document.removeEventListener('keydown', onKey), { once: true });

  const check = $('#check');
  if (check) {
    check.onclick = async () => {
      if (g.frame > 20000) { $('#checkout').textContent = ' Runs up to 20000 frames can be checked; restart and try a shorter run.'; return; }
      check.disabled = true; $('#checkout').textContent = ' running the Python game...';
      try {
        const frames = Math.max(1, g.frame);
        const rec = await api('/run', { body: { seed, frames, every: 10, keys } });
        const { checked, first } = replay(Game, rec);
        $('#checkout').innerHTML = first ? ` <span class="err">Differs: ${esc(first)}</span>`
          : ` <span class="ok">Identical: ${checked} snapshots over ${frames} frames match the Python.</span>`;
      } catch (err) { $('#checkout').innerHTML = ` <span class="err">${esc(err.message)}</span>`; }
      check.disabled = false;
    };
  }
  render();
});
