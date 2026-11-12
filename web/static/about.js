// About page: what the project is, how to run the desktop game, the web app and the static site, and credits (README).
import { route, app, isStatic } from './core.js';

route('about', () => {
  app().innerHTML = `
  <p class="kicker">About</p>
  <h1>Self-Aware Game</h1>
  <p class="lead">A Python simulation featuring self-aware game characters who realize they're in a game. The project has a
  meta "game within a game" structure: a self-aware snake game exists inside a larger world with a roaming self-aware
  character. Written with pygame.</p>

  <h2>What happens</h2>
  <ul>
    <li><b>Alex</b> (<code>modules/character.py</code>) idles, walks, thinks, investigates buildings and gets confused, with a
      library of existential and fourth-wall thoughts. Press <kbd>E</kbd> and it talks to you.</li>
    <li><b>The snake</b> (<code>modules/snake_game.py</code>, <code>snake_ai.py</code>) plays itself. Each meal raises its
      awareness by 0.5 and its AI gets smarter from level 5. From level 8 a glitch can appear; eating it (or pressing
      <kbd>T</kbd>) starts Matrix mode, and 4.5 seconds later the snake transcends into the world as a
      <b>transcended entity</b> (<code>modules/entities.py</code>), with falling code across the whole screen.</li>
    <li>The world (<code>main.py</code>, <code>modules/world.py</code>) notices when Alex comes near the snake game and when
      Alex meets the escaped snake.</li>
  </ul>

  <h2>This web version</h2>
  <p>The game here is the Python code ported to JavaScript (<code>sim_world.js</code>, <code>sim_character.js</code>,
  <code>sim_snake.js</code>, <code>py_random.js</code>), tested frame for frame against seeded runs of the Python. There is
  no language model anywhere in the project: every thought is one of the lines written in the code.
  ${isStatic() ? 'This static site needs no server; only "Check with Python" on the World page needs the local app.' : ''}</p>
  <div class="callout">While building this site, several bugs in the Python were fixed: the snake game was updated and drawn
  twice per frame; the snake died when moving into the cell its tail was leaving (most games ended at score 1); Alex could
  never get "near" the 500-pixel snake game, so it never noticed or investigated it; Alex's idle thoughts stopped after the
  first one; the debug FPS always read 0; and under arrow-key control the snake moved 60 cells a second. See SESSION_LOG.md.</div>

  <h2>Run the desktop game</h2>
  <pre>pip install -r requirements.txt     # pygame
python main.py                      # or: python main.py --seed 0   (replayable run)</pre>
  <p>Keys: arrows steer the snake (after <kbd>A</kbd> turns its AI off), <kbd>Space</kbd> pauses the snake game,
  <kbd>R</kbd> restarts it after game over, <kbd>+</kbd>/<kbd>-</kbd> change its speed, <kbd>T</kbd> triggers transcendence
  (awareness 8+), <kbd>P</kbd> pauses everything, <kbd>D</kbd> shows debug info, <kbd>E</kbd> talks to Alex, <kbd>M</kbd>
  forces Matrix mode.</p>

  <h2>Run the web app</h2>
  <pre>pip install -r requirements-web.txt
python run_web.py          # http://127.0.0.1:8142</pre>
  <p>Build the static site (what GitHub Pages serves) with <code>python scripts/build_static.py</code>; run the tests with
  <code>python -m pytest -q</code> (the web tests include the node engine test).</p>

  <h2>Credits</h2>
  <p>By George Dickinson. MIT licence. Built with AI assistance from
  <a href="https://claude.com/" target="_blank" rel="noopener">Claude (Anthropic)</a>.
  Source: <a href="https://github.com/gddickinson/self-aware_game" target="_blank" rel="noopener">github.com/gddickinson/self-aware_game</a>.</p>`;
});
