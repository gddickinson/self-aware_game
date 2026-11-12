// Inspector panel for the World page: the selected character's state as the Python objects hold it
// (SelfAwareCharacter, SnakeGame, TranscendedEntity), plus the web-only event log of this run.
import { esc } from './core.js';
import { STATES } from './sim_character.js';

const row = (k, v, title = '') => `<div${title ? ` title="${esc(title)}"` : ''}><span>${esc(k)}</span><b>${v}</b></div>`;
const xy = p => (p ? `(${p[0].toFixed(1)}, ${p[1].toFixed(1)})` : '-');
const DIRS = ['right', 'down', 'left', 'up'];
const dirName = d => ({ '1,0': 'right', '0,1': 'down', '-1,0': 'left', '0,-1': 'up' }[d.join(',')] || d.join(','));
const meter = (v, max, label) => `<div class="meter" role="meter" aria-label="${esc(label)}" aria-valuemin="0" aria-valuemax="${max}" aria-valuenow="${v}">
  <i style="width:${Math.min(100, (v / max) * 100)}%"></i><em>${v.toFixed(1)} / ${max}</em></div>`;
const thought = (t, timer) => (t ? `<p class="thought">"${esc(t)}"<small>${timer > 0 ? `shown for ${(timer / 60).toFixed(1)} s more` : 'no longer shown'}</small></p>`
  : '<p class="thought mute">(no current thought)</p>');

function alex(g) {
  const c = g.character;
  return `<h3>Alex <small>SelfAwareCharacter</small></h3>
  <p class="small mute">Self-awareness</p>${meter(c.selfAwareness, 10, 'self-awareness')}
  ${thought(c.currentThought, c.thoughtTimer)}
  <div class="readout">
    ${row('state', esc(c.state), STATES.join(' / '))}${row('time in state', ['IDLE', 'THINKING', 'CONFUSED'].includes(c.state) ? `${c.stateTimer} / ${c.stateDuration} frames` : `${c.stateTimer} frames`)}
    ${row('position', xy(c.position))}${row('facing', DIRS[c.direction])}
    ${row('target', xy(c.target))}${row('near snake game', c.isNearBuilding('Snake Game') ? 'yes' : 'no')}
    ${row('noticed snake game', c.noticedSnakeGame ? 'yes' : 'no')}${row('animation frame', c.animFrame)}
  </div>
  <p class="hint">Self-awareness is fixed at 8.5 in the Python ("starts high as character is already self-aware").
  Press <kbd>E</kbd> or click Alex twice to interact.</p>`;
}

function snake(g) {
  const s = g.snake;
  const unlocked = s.thoughts.map((t, i) => `<li class="${i <= Math.trunc(s.awareness) ? 'on' : ''}">${i}: ${esc(t)}</li>`).join('');
  return `<h3>Snake <small>SnakeGame</small></h3>
  <p class="small mute">Awareness (+0.5 per food; thoughts at 1, 3, 5, 7, 9; glitch can appear from 8)</p>${meter(s.awareness, 10, 'snake awareness')}
  ${thought(s.currentThought, s.thoughtTimer)}
  <div class="readout">
    ${row('score', s.score)}${row('length', s.snake.length)}
    ${row('control', s.aiControlled ? 'AI' : 'player (arrows)')}${row('moves every', `${s.aiSpeed} frames`)}
    ${row('heading', dirName(s.direction))}${row('food', `(${s.food.join(', ')})`)}
    ${row('glitch', s.glitch ? `(${s.glitch.join(', ')})` : 'none')}${row('matrix mode', s.matrixMode ? `on (${s.matrixTimer})` : 'off')}
    ${row('transcended', s.transcended ? 'yes' : 'no')}${row('state', s.gameOver ? 'game over' : s.paused ? 'paused' : 'playing')}
  </div>
  <p class="small mute">Thought ladder (by awareness level)</p><ol class="ladder">${unlocked}</ol>`;
}

function entity(g, i) {
  const e = g.entities[i];
  if (!e) return '<p class="mute">That entity is not in this run.</p>';
  return `<h3>Transcended entity ${i + 1} <small>TranscendedEntity</small></h3>
  ${thought(e.thought, e.thoughtTimer)}
  <div class="readout">
    ${row('position', xy(e.position))}${row('heading', dirName(e.direction))}
    ${row('target', xy(e.target))}${row('retarget in', `${e.timer} frames`)}
  </div>
  <p class="hint">The snake's head, escaped from the snake game into the world. It wanders to random targets; when Alex
  touches it, both speak.</p>`;
}

function world(g) {
  return `<h3>World <small>main.SelfAwareGame</small></h3>
  <div class="readout">
    ${row('frame', g.frame)}${row('game time', `${(g.frame / 60).toFixed(1)} s`)}
    ${row('seed', g.seed)}${row('paused (P)', g.paused ? 'yes' : 'no')}
    ${row('world matrix', g.matrixMode ? `on (${g.matrixTimer})` : 'off')}${row('entities', g.entities.length)}
  </div>`;
}

// Tab buttons for every selectable thing in this run.
export function tabs(g, selected) {
  const items = [['alex', 'Alex'], ['snake', 'Snake'], ...g.entities.map((_, i) => [`entity${i}`, `Entity ${i + 1}`]), ['world', 'World']];
  return items.map(([k, label]) => `<button type="button" data-sel="${k}" class="${k === selected ? 'on' : ''}" aria-pressed="${k === selected}">${label}</button>`).join('');
}

export function inspect(g, selected) {
  if (selected === 'snake') return snake(g);
  if (selected === 'world') return world(g);
  if (selected.startsWith('entity')) return entity(g, +selected.slice(6));
  return alex(g);
}

export function eventLog(g, n = 40) {
  const ev = g.events.slice(-n).reverse();
  if (!ev.length) return '<li class="mute">Nothing yet: press play.</li>';
  return ev.map(e => `<li><span class="mono">${(e.frame / 60).toFixed(1)}s</span> <b>${esc(e.who)}</b> ${esc(e.text)}</li>`).join('');
}
