// Verify page: replay a seeded run recorded from the Python game (/api/reference) in the browser engine and compare.
import { route, api, app, esc, isStatic } from './core.js';
import { Game } from './sim_world.js';
import { replay } from './sim_snapshot.js';

const firstFrame = (rec, test) => (rec.snaps.find(test) || {}).frame ?? '-';

route('verify', async () => {
  app().innerHTML = '<p class="mute">Replaying the Python run...</p>';
  const rec = await api('/reference');
  const t0 = performance.now();
  const { checked, first } = replay(Game, rec);
  const ms = performance.now() - t0;
  const last = rec.snaps.at(-1);
  const milestones = [
    ['Alex notices the snake game', firstFrame(rec, s => s.char.noticed)],
    ['Snake reaches awareness 5', firstFrame(rec, s => s.snake.awareness >= 5)],
    ['Glitch appears', firstFrame(rec, s => s.snake.glitch)],
    ['Snake enters Matrix mode', firstFrame(rec, s => s.snake.matrix)],
    ['Snake transcends into the world', firstFrame(rec, s => s.snake.transcended)],
  ];
  app().innerHTML = `
  <p class="kicker">Browser engine vs Python</p>
  <h1 class="glow">Verify</h1>
  <p class="lead">This run was recorded from the real desktop code (<code>main.SelfAwareGame</code>, seed ${rec.seed}, run
  headless${isStatic() ? ' when this site was built' : ' just now by the local server'}). Your browser has just replayed it with
  the JavaScript engine and compared the full state every ${rec.every} frames.</p>
  <div class="callout ${first ? '' : 'a'}">${first
    ? `<b class="err">Mismatch.</b> ${esc(first)}`
    : `<b class="ok">Identical.</b> ${checked} snapshots over ${rec.frames} frames (${(rec.frames / 60).toFixed(0)} s of game time)
       match, and the random generators are still in step afterwards. Replay took ${ms.toFixed(0)} ms.`}</div>
  <div class="two">
    <div class="panel"><h3>Milestones in this run (Python record)</h3>
      <table><thead><tr><th>Event</th><th>by frame</th></tr></thead><tbody>
      ${milestones.map(([k, f]) => `<tr><td>${k}</td><td class="mono">${f}</td></tr>`).join('')}</tbody></table>
      <p class="hint">Frames are checked every ${rec.every}, so each event happened at or before the frame shown.</p></div>
    <div class="panel"><h3>Compared at every snapshot</h3>
      <p class="small">Alex: position, state and timer, facing, target, thought and timer, whether it has noticed the snake
      game, animation frame. Snake: every body cell, heading, food, score, awareness, AI/manual, speed, glitch, Matrix mode,
      transcended, thought, first Matrix-rain characters. Escaped entities: position, heading, target, thought, code stream.
      World: pause, Matrix mode and rain, dialogue messages.</p>
      <p class="small mute">End state: snake score ${last.snake.score}, awareness ${last.snake.awareness}, ${last.entities.length} escaped
      entit${last.entities.length === 1 ? 'y' : 'ies'}, ${last.dialogue.length} dialogue message(s).</p></div>
  </div>
  <p class="small mute">The repository's node test (<code>web/static/sim_engine.test.mjs</code>) does the same for five longer runs,
  including every key the desktop game handles.</p>`;
});
