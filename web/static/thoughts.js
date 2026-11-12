// Thoughts page: every line the characters can think or say, from the Python's text libraries (/api/texts).
import { route, api, app, esc } from './core.js';
import { LINES } from './sim_texts.js';

// Alex's thought library is grouped by comments in modules/character.py (_initialize_thoughts).
const GROUPS = [['Existential thoughts', 5], ['Observations about the world', 4], ['Meta-awareness', 5], ['Fourth-wall breaks', 5]];
const ul = (items, label = null) => `<ul class="quotes">${items.map((t, i) => `<li>${label ? `<b>${esc(label(i))}</b>` : ''}${esc(t)}</li>`).join('')}</ul>`;

route('thoughts', async () => {
  const t = await api('/texts');
  let at = 0;
  const groups = GROUPS.map(([name, n]) => { const part = t.character.slice(at, at + n); at += n; return `<h3>${name}</h3>${ul(part)}`; }).join('')
    + (at < t.character.length ? `<h3>More</h3>${ul(t.character.slice(at))}` : '');
  app().innerHTML = `
  <p class="kicker">Dialogue and thought system</p>
  <h1 class="glow">Thoughts</h1>
  <p class="lead">What the characters think and say, exactly as written in the Python. Thoughts appear in bubbles over the
  thinker for 3-5 seconds (the snake's for 5, or 10 around the glitch); remarks to the world go to the dialogue box at the bottom of the screen.</p>
  <div class="two">
    <div class="panel">
      <h2>Alex</h2>
      <p class="small mute">A random one of these when Alex switches to thinking, and now and then while idle.</p>
      ${groups}
      <h3>Near the snake game</h3>
      <p class="small mute">After investigating the snake game's building.</p>${ul(t.observations)}
      <h3>When you interact (E)</h3>${ul(t.fourthWall)}
      <h3>Fixed lines</h3>
      ${ul([LINES.CONFUSED, LINES.NOTICE_SNAKE, LINES.MEET_ENTITY_CHAR])}
      <p class="small mute">When confused; when it first comes near the snake game (said in the dialogue box); when it bumps into an escaped snake.</p>
    </div>
    <div class="panel">
      <h2>The snake</h2>
      <p class="small mute">Awareness rises by 0.5 per food eaten. At awareness 1, 3, 5, 7 and 9 (and at random moments) the
      snake thinks the line for its current level.</p>
      ${ul(t.snake, i => `level ${i}`)}
      <h3>Transcendence</h3>
      ${ul([LINES.GLITCH, LINES.MATRIX, LINES.FREE, LINES.MEET_ENTITY])}
      <p class="small mute">When the glitch appears (awareness 8+, 30% chance per meal); on eating it (Matrix mode); on escaping into
      the world; and, as an escaped entity, when Alex walks into it. The world announces: "${esc(LINES.TRANSCEND_MSG)}"</p>
      <h3>Desktop controls panel</h3>${ul(t.controls)}
    </div>
  </div>`;
});
